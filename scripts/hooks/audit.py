#!/usr/bin/env python3
"""Stop hook. When a desk ran interactively (NEWSROOM_DESK set, no runner), append the RUN line
the runner would have written, so an interactive session in the vault is logged too.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _lib import append_audit, read_event, vault_root  # noqa: E402

event = read_event()
desk = os.environ.get("NEWSROOM_DESK", "").strip()
if not desk or os.environ.get("NEWSROOM_RUNNER") == "1":
    sys.exit(0)
append_audit(vault_root(event), "RUN", desk, f"interactive session ended, run={os.environ.get('NEWSROOM_RUN', 'unknown')}")
sys.exit(0)
