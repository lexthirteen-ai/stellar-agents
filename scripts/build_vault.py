#!/usr/bin/env python3
"""build_vault.py: generate the vault's map files from kit.json, the one source of the map.

    python3 scripts/build_vault.py            # write newsroom/governance/registry.json and newsroom/Constellation.canvas
    python3 scripts/build_vault.py --check    # exit 1 if either file differs from what kit.json would generate

Each registry goal is copied from the star's charter Goal line, so the charter stays the only place a goal is written.
Draco sits at the center of the canvas, the owner above it, every other star on a ring around it.
The arrows are the hands_to lines in kit.json. Ascension stars get their own color.
"""
import json, math, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = os.path.join(ROOT, "newsroom", "governance", "registry.json")
CANVAS = os.path.join(ROOT, "newsroom", "Constellation.canvas")
NOTE = ("One row per star, generated from kit.json by scripts/build_vault.py. goal is copied from the charter's Goal line. "
        "write_zones are the only paths the star may create or modify, relative to the vault root. If a charter and this file disagree, this file wins.")
COLOR = {"core": "5", "ascension": "6"}


def goal_of(star_path):
    p = os.path.join(ROOT, star_path, "SKILL.md")
    if not os.path.exists(p):
        return ""
    body = open(p, encoding="utf-8").read()
    m = re.search(r"^## 1\. Goal\s*\n(.*?)(?=^## )", body, re.S | re.M)
    if not m:
        return ""
    lines = [l.strip() for l in m.group(1).splitlines() if l.strip() and not l.strip().startswith(">")]
    return lines[0] if lines else ""


def tools_of(star):
    p = os.path.join(ROOT, star["path"], "SKILL.md")
    if os.path.exists(p):
        m = re.search(r"^tools:\s*(.+)$", open(p, encoding="utf-8").read(), re.M)
        if m:
            return [t.strip() for t in m.group(1).split(",") if t.strip()]
    return list(star["tools"])


def registry(kit):
    desks = []
    for s in kit["stars"]:
        desks.append({
            "id": s["id"],
            "goal": goal_of(s["path"]),
            "role": s["role"],
            "tier": s["tier"],
            "cadence": s["cadence"],
            "status": "active",
            "tools": tools_of(s),
            "write_zones": s["write_zones"],
            "receives_from": s["receives_from"],
            "hands_to": s["hands_to"],
            "never_autonomous_ack": True,
        })
    return {"$schema_note": NOTE, "desks": desks}


def canvas(kit):
    stars = kit["stars"]
    center = next(s for s in stars if s["star"] == "draco")
    ring = [s for s in stars if s is not center]
    W, H = 300, 180
    nodes = [{"id": "owner", "type": "text", "text": "# You\nThe brief ends here. Tick the box. Send by hand.",
              "x": -W // 2, "y": -700, "width": W, "height": 120, "color": "4"}]
    pos = {center["id"]: (-W // 2, -H // 2)}
    radius = 900
    for i, s in enumerate(ring):
        a = -math.pi / 2 + (2 * math.pi * (i + 0.5) / len(ring))
        pos[s["id"]] = (int(radius * math.cos(a)) - W // 2, int(radius * math.sin(a)) - H // 2 + 200)
    for s in stars:
        x, y = pos[s["id"]]
        nodes.append({"id": s["id"], "type": "file", "file": f".claude/skills/{s['id']}/SKILL.md",
                      "x": x, "y": y, "width": W, "height": H, "color": COLOR.get(s["tier"], "5")})
        zones = ", ".join(s["write_zones"])
        nodes.append({"id": s["id"] + "-note", "type": "text",
                      "text": f"**{s['star'].capitalize()}** ({s['tier']}) {s['cadence']}\nwrites {zones}",
                      "x": x, "y": y + H + 10, "width": W, "height": 80, "color": COLOR.get(s["tier"], "5")})
    edges = []
    for s in stars:
        for t in s["hands_to"]:
            edges.append({"id": f"{s['id']}->{t}", "fromNode": s["id"], "toNode": t, "toEnd": "arrow"})
    return {"nodes": nodes, "edges": edges}


def dump(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def main():
    kit = json.load(open(os.path.join(ROOT, "kit.json")))
    want = {REG: dump(registry(kit)), CANVAS: dump(canvas(kit))}
    if "--check" in sys.argv:
        bad = [os.path.relpath(p, ROOT) for p, t in want.items() if not os.path.exists(p) or open(p, encoding="utf-8").read() != t]
        for b in bad:
            print(f"FAIL {b} is out of date with kit.json. Run: python3 scripts/build_vault.py")
        return 1 if bad else 0
    for p, t in want.items():
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8").write(t)
        print(f"wrote {os.path.relpath(p, ROOT)}")
    missing = [s["id"] for s in kit["stars"] if not goal_of(s["path"])]
    if missing:
        print("note: no Goal line yet for " + ", ".join(missing))
    return 0


if __name__ == "__main__":
    sys.exit(main())
