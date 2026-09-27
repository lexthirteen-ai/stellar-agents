#!/usr/bin/env python3
"""PreToolUse hook for Write, Edit, MultiEdit, NotebookEdit.

When a desk is running (NEWSROOM_DESK is set), a write outside that desk's write_zones in
governance/registry.json is blocked. The registry wins over the charter's tools line, in code.
With no desk set, the owner is at the keyboard and this hook stays out of the way.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _lib import block, in_zone, read_event, registry, tool_path, vault_root  # noqa: E402

event = read_event()
desk = os.environ.get("NEWSROOM_DESK", "").strip()
if not desk:
    sys.exit(0)
path = tool_path(event)
if not path:
    sys.exit(0)
vault = vault_root(event)
rows = registry(vault)
row = rows.get(desk)
if row is None:
    block(f"write-zone: desk '{desk}' is not in governance/registry.json. An unregistered desk writes nothing.")
rel = os.path.relpath(os.path.abspath(path), vault)
if rel.startswith(".."):
    block(f"write-zone: {path} is outside the vault. {desk} writes only inside her write zones: {', '.join(row['write_zones'])}.")
if not in_zone(rel, row.get("write_zones", [])):
    block(f"write-zone: {rel} is outside {desk}'s write zones ({', '.join(row['write_zones'])}). The registry wins. Write inside a zone or stop and say why you cannot.")
sys.exit(0)
