"""Shared pieces for the Newsroom hooks and the runner. Standard library only."""
import datetime
import json
import os
import re
import sys

PROV = re.compile(r"^provenance: desk=[a-z0-9-]+ \| run=\S+ \| trigger=\S+ \| inputs=.+$")


def read_event():
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def vault_root(event=None):
    v = os.environ.get("NEWSROOM_VAULT")
    if v:
        return os.path.abspath(v)
    cwd = (event or {}).get("cwd") or os.getcwd()
    d = os.path.abspath(cwd)
    while True:
        if os.path.exists(os.path.join(d, "NEWSROOM.md")) or os.path.isdir(os.path.join(d, "governance")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return os.path.abspath(cwd)
        d = parent


def registry(vault):
    p = os.path.join(vault, "governance", "registry.json")
    try:
        return {d["id"]: d for d in json.load(open(p, encoding="utf-8"))["desks"]}
    except Exception:
        return {}


def now_stamp():
    return _now().strftime("%Y-%m-%d %H:%M")


def _now():
    """The wall clock, or NEWSROOM_NOW (ISO, UTC) when a simulation or an eval pins the date."""
    pinned = os.environ.get("NEWSROOM_NOW")
    if pinned:
        return datetime.datetime.strptime(pinned, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
    return datetime.datetime.now(datetime.timezone.utc)


def now_iso():
    return _now().strftime("%Y-%m-%dT%H:%M:%SZ")


def append_audit(vault, event, desk, note):
    """Append one line inside the ## Log fence of governance/audit-log.md. Never edits an existing line."""
    p = os.path.join(vault, "governance", "audit-log.md")
    line = f"{now_stamp()} | {event} | {desk} | {note}\n"
    if not os.path.exists(p):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8").write("# Audit Log\n\nAppend only.\n\n## Log\n\n```\n" + line + "```\n")
        return line
    text = open(p, encoding="utf-8").read()
    if text.rstrip().endswith("```"):
        text = text.rstrip()[:-3].rstrip("\n") + "\n" + line + "```\n"
    else:
        text = text.rstrip("\n") + "\n" + line
    open(p, "w", encoding="utf-8").write(text)
    return line


def block(msg):
    sys.stderr.write(msg.rstrip() + "\n")
    sys.exit(2)


def tool_path(event):
    ti = event.get("tool_input") or {}
    return ti.get("file_path") or ti.get("notebook_path") or ""


def in_zone(rel, zones):
    rel = rel.replace(os.sep, "/")
    for z in zones:
        z = z.replace(os.sep, "/")
        if z.endswith("/") and rel.startswith(z):
            return True
        if rel == z:
            return True
    return False
