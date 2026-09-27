#!/usr/bin/env python3
"""copydesk.py: check a drafted item against its output contract. Hard fail on drift.

Usage:
    python scripts/copydesk.py outputs/drafts/2026-09-22-post.md
    python scripts/copydesk.py --channels linkedin,newsletter,threads outputs/drafts/*.md
    python scripts/copydesk.py --move --log governance/audit-log.md outputs/drafts/*.md

--move  moves a passing file to outputs/staged/ and a failing one to outputs/rejected/ with
        "## Rejected because" and the rules appended, then Vesper's provenance line. Paths are
        resolved next to the draft's outputs/ folder.
--log   appends one RUN or REJECTED line per file to the given audit log.

Contract (see .agents/lyra/SKILL.md):
    line 1   ### ITEM <kind> | <channel> | <slot>
    line 2   chars: <real character count of the body>
    line 3   ---
    line 4   [HEADLINE, REWRITE ME: <draft>]       the human only marker, must be intact
    body     everything after line 4 up to the provenance line
    last     provenance: desk=... | run=... | trigger=... | inputs=...

Exit 0 when every file passes. Exit 1 when any fails, with the rule named.
The script is the judge. It does not rewrite anything.
"""
import datetime
import os
import re
import shutil
import sys

DEFAULT_CHANNELS = {"linkedin", "newsletter", "threads", "blog", "email-draft"}
MARKER = re.compile(r"^\[HEADLINE, REWRITE ME: .+\]$")
PROV = re.compile(r"^provenance: desk=[a-z0-9-]+ \| run=\S+ \| trigger=\S+ \| inputs=.+$")


def check(path, channels):
    fails = []
    lines = open(path, encoding="utf-8").read().rstrip("\n").split("\n")
    if len(lines) < 6:
        return ["file too short to contain the contract"]

    m = re.match(r"^### ITEM (\S+) \| (\S+) \| (\S+)$", lines[0])
    if not m:
        fails.append("line 1 must be '### ITEM <kind> | <channel> | <slot>'")
    else:
        channel = m.group(2).lower()
        if channel not in channels:
            fails.append(f"channel '{channel}' is not on the allowed list")

    cm = re.match(r"^chars: (\d+)$", lines[1])
    if not cm:
        fails.append("line 2 must be 'chars: <number>'")

    if lines[2].strip() != "---":
        fails.append("line 3 must be '---'")

    if not MARKER.match(lines[3].strip()):
        fails.append("line 4 human only marker missing or finalized; must read [HEADLINE, REWRITE ME: ...]")

    if not PROV.match(lines[-1].strip()):
        fails.append("last line must be a provenance line with desk=, run=, trigger=, inputs=")

    body = "\n".join(lines[4:-1]).strip()
    if not body:
        fails.append("body is empty")
    if cm:
        declared = int(cm.group(1))
        actual = len(body)
        if declared != actual:
            fails.append(f"chars mismatch: declared {declared}, actual {actual}. Count it, never quote it.")
    return fails


def _now():
    """The wall clock, or NEWSROOM_NOW (ISO, UTC) when a simulation or an eval pins the date."""
    pinned = os.environ.get("NEWSROOM_NOW")
    if pinned:
        return datetime.datetime.strptime(pinned, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
    return datetime.datetime.now(datetime.timezone.utc)


def outputs_root(path):
    """The outputs/ folder this draft lives under, or its parent folder if none."""
    d = os.path.dirname(os.path.abspath(path))
    while d and os.path.basename(d) != "outputs" and os.path.dirname(d) != d:
        d = os.path.dirname(d)
    return d if os.path.basename(d) == "outputs" else os.path.dirname(os.path.abspath(path))


def move(path, fails):
    root = outputs_root(path)
    now = _now().strftime("%Y-%m-%dT%H:%M:%SZ")
    if fails:
        dest = os.path.join(root, "rejected", os.path.basename(path))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        body = open(path, encoding="utf-8").read().rstrip("\n")
        extra = "\n\n## Rejected because\n\n" + "\n".join(f"- {f}" for f in fails)
        m = re.search(r"desk=([a-z0-9-]+)", body.splitlines()[-1] if body else "")
        writer = m.group(1) if m else "unknown-writer"
        prov = f"\nprovenance: desk=vesper-copy-desk | run={now} | trigger={writer} | inputs={os.path.relpath(path)}\n"
        open(dest, "w", encoding="utf-8").write(body + extra + "\n" + prov)
        os.remove(path)
    else:
        dest = os.path.join(root, "staged", os.path.basename(path))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.move(path, dest)
    return dest


def log(logfile, path, fails):
    now = _now().strftime("%Y-%m-%d %H:%M")
    event = "REJECTED" if fails else "RUN"
    note = f"{os.path.relpath(path)} staged" if not fails else f"{os.path.relpath(path)} rejected, {fails[0]}"
    text = open(logfile, encoding="utf-8").read()
    line = f"{now} | {event} | vesper-copy-desk | {note}\n"
    # The log ends its ## Log section with a closing fence. Append inside it when present.
    if text.rstrip().endswith("```"):
        text = text.rstrip()[:-3].rstrip("\n") + "\n" + line + "```\n"
    else:
        text = text.rstrip("\n") + "\n" + line
    open(logfile, "w", encoding="utf-8").write(text)


def main(argv):
    channels = set(DEFAULT_CHANNELS)
    paths = []
    do_move = False
    logfile = None
    i = 0
    while i < len(argv):
        if argv[i] == "--channels":
            channels = {c.strip().lower() for c in argv[i + 1].split(",") if c.strip()}
            i += 2
        elif argv[i] == "--move":
            do_move = True
            i += 1
        elif argv[i] == "--log":
            logfile = argv[i + 1]
            i += 2
        else:
            paths.append(argv[i])
            i += 1
    if not paths:
        print(__doc__)
        return 2
    bad = 0
    for p in paths:
        fails = check(p, channels)
        if fails:
            bad += 1
            print(f"REJECTED {p}")
            for f in fails:
                print(f"  - {f}")
        else:
            print(f"STAGED {p}")
        if logfile:
            log(logfile, p, fails)
        if do_move:
            print(f"  -> {move(p, fails)}")
    print(f"\n{len(paths) - bad} staged, {bad} rejected")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
