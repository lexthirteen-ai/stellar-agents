#!/usr/bin/env python3
"""PostToolUse hook for Write, Edit, MultiEdit.

Any file written under outputs/ or Daily/ (README.md aside) must end with a provenance line. A file under
outputs/drafts/ must also pass copydesk.py. The write has already happened when this runs, so a
failure is reported back to the desk with the rule named, and the desk fixes the file before it
hands off. This is how a wrong character count gets corrected at write time instead of at review.
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _lib import PROV, block, read_event, tool_path, vault_root  # noqa: E402

event = read_event()
path = tool_path(event)
if not path or not os.path.isfile(path):
    sys.exit(0)
vault = vault_root(event)
rel = os.path.relpath(os.path.abspath(path), vault).replace(os.sep, "/")
if not rel.startswith(("outputs/", "Daily/")) or os.path.basename(rel) == "README.md" or not rel.endswith(".md"):
    sys.exit(0)
lines = [l for l in open(path, encoding="utf-8").read().splitlines() if l.strip()]
if not lines or not PROV.match(lines[-1].strip()):
    block(f"provenance: {rel} does not end with a provenance line. Last line must be: provenance: desk=<id> | run=<ISO datetime from the trigger message> | trigger=<who> | inputs=<paths>. Fix the file now.")
if rel.startswith("outputs/drafts/"):
    scripts = os.environ.get("NEWSROOM_SCRIPTS") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    copydesk = os.path.join(scripts, "copydesk.py")
    if os.path.exists(copydesk):
        r = subprocess.run([sys.executable, copydesk, path], capture_output=True, text=True)
        if r.returncode != 0:
            block("copydesk: " + r.stdout.strip() + "\nFix the file so every rule passes, then hand off. Do not finalize the first line.")
sys.exit(0)
