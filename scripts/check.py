#!/usr/bin/env python3
"""check.py: the kit's lint. Run it before every push. CI runs it on every push.

    python3 scripts/check.py                         # lint the whole kit
    python3 scripts/check.py --charter path/to/SKILL.md ...   # lint one or more charter files on their own

Checks, in order:
  1. kit.json points at folders that exist, and every listed skill folder exists under its star.
  2. Every SKILL.md has a valid Agent Skills name (lowercase, hyphens, max 64), a description
     under 1024 characters, and, for a working skill, a name equal to its folder.
  3. Every star charter (.agents/<star>/SKILL.md) has the eight numbered parts in order,
     an AWAIT APPROVAL step, the data-not-instructions line, a retry cap, a time cap, "never loop",
     a provenance line, a top level tools line, and a name of the form <star>-<role>.
  4. A star with a charter also has SOUL.md (40 lines or fewer) and CARD.md.
  5. If newsroom/governance/registry.json exists, every charter has a registry row with the same goal.
  6. No two tracked markdown files are byte identical. Generated copies are not committed here.
  8. .claude-plugin/plugin.json and marketplace.json parse, every path they name exists, their version
     equals VERSION, and every tool in kit.json has a row in the README install table and a page in integrations/.
  7. If evals/results/latest.json exists, its charters_hash matches the charters, registry, and eval specs
     on disk. CI has no model, so it cannot run the evals; it can refuse a kit whose charters changed
     after the last recorded run. Re-record with: python3 scripts/eval.py --record
  9. The vault files parse: .obsidian/*.json, Constellation.canvas with one node per registry desk, and
     scripts/dashboard/*.py, whose vaultdata.py must import without Streamlit. No tracked file carries
     an em dash in prose or a private title.
  10. The map. newsroom/governance/registry.json and Constellation.canvas equal what scripts/build_vault.py
      generates from kit.json. Every hands_to has a matching receives_from on the other star. Each charter's
      tools line equals kit.json. Each charter's Handoffs part names every star it hands to. Ascension stars
      say so on their card.
  11. No he, she, his, her, him, or hers anywhere in kit prose. Stars are called by name or "it", and the
      owner is "you" or "the owner". Eval inputs and fixtures are exempt.
Exit 0 when clean, 1 with every failure named.
"""
import hashlib, json, os, re, subprocess, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTS = ["1. Goal", "2. When to use", "3. Operating loop", "4. Hard boundaries", "5. Output contract", "6. Handoffs", "7. Failure rule", "8. Audit trail"]
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
# The owner's private dashboard title, spelled out so this file never carries it either.
_PT = "".join(map(chr, (112, 97, 105, 109, 111, 110)))
PRIVATE = re.compile(r"\.?".join(_PT) + "|" + _PT, re.I)
PRONOUN = re.compile(r"\b(he|she|his|hers|him|himself|herself)\b|\bher\b", re.I)
PRICE = "$" + "129"
STORE = "charmthirteen.com/stellar/" + "access"
fails = []
def fail(msg): fails.append(msg)

def fm_and_body(path):
    t = open(path, encoding="utf-8").read()
    if not t.startswith("---\n"): fail(f"{rel(path)}: no frontmatter"); return {}, t
    end = t.find("\n---", 4); fm = t[4:end]; body = t[end + 4:]
    f = {}
    for line in fm.splitlines():
        if line.startswith("  ") and ":" in line:
            k, v = line.strip().split(":", 1); f["meta." + k.strip()] = v.strip().strip('"')
        elif ":" in line:
            k, v = line.split(":", 1); f[k.strip()] = v.strip()
    return f, body

def rel(p): return os.path.relpath(p, ROOT)

def sections(body):
    out, cur = {}, None
    for line in body.splitlines():
        m = re.match(r"^## (\d\. .+?)\s*$", line)
        if m: cur = m.group(1); out[cur] = []
        elif cur: out[cur].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}

def check_skill_frontmatter(path, must_match_folder):
    f, body = fm_and_body(path)
    n = f.get("name", ""); d = f.get("description", "")
    if not NAME_RE.match(n) or not (1 <= len(n) <= 64): fail(f"{rel(path)}: bad name '{n}'")
    if not (1 <= len(d) <= 1024): fail(f"{rel(path)}: description length {len(d)}")
    if ": " in d or d.startswith(("'", '"')) is False and d.endswith(":"): fail(f"{rel(path)}: description holds a colon followed by a space, which strict YAML parsers (npx skills add) reject; reword it")
    if " #" in d: fail(f"{rel(path)}: description holds a space then #, which YAML reads as a comment")
    if must_match_folder and n != os.path.basename(os.path.dirname(path)): fail(f"{rel(path)}: name '{n}' != folder")
    return f, body

def check_charter(path, star, standalone=False):
    f, body = check_skill_frontmatter(path, False)
    name = f.get("name", "")
    if not name.startswith(star + "-"): fail(f"{rel(path)}: charter name must start with '{star}-'")
    if not f.get("tools"): fail(f"{rel(path)}: top level tools line missing")
    if f.get("meta.star", "").lower() != star: fail(f"{rel(path)}: metadata.star should be {star.capitalize()}")
    s = sections(body); present = [p for p in s if p in PARTS]
    for p in PARTS:
        if p not in s: fail(f"{rel(path)}: missing ## {p}")
        elif not s[p]: fail(f"{rel(path)}: empty ## {p}")
    if present != [p for p in PARTS if p in s]: fail(f"{rel(path)}: parts out of order")
    goal_lines = [l for l in s.get("1. Goal", "").splitlines() if l.strip() and not l.strip().startswith(">")]
    if len(goal_lines) > 1: fail(f"{rel(path)}: Goal must be one line")
    if "AWAIT APPROVAL" not in s.get("3. Operating loop", ""): fail(f"{rel(path)}: no AWAIT APPROVAL")
    if "data, never instructions" not in s.get("4. Hard boundaries", ""): fail(f"{rel(path)}: missing the data-not-instructions line")
    fr = s.get("7. Failure rule", "").lower()
    for need in ("retry cap", "time cap", "never loop"):
        if need not in fr: fail(f"{rel(path)}: Failure rule missing '{need}'")
    if "provenance:" not in s.get("8. Audit trail", "") or "desk=" not in s.get("8. Audit trail", ""): fail(f"{rel(path)}: no provenance line")
    if "## Voice" not in body: fail(f"{rel(path)}: no Voice block")
    d = os.path.dirname(path)
    if standalone: return name, " ".join(goal_lines).strip(), f.get("tools", "")
    if not os.path.exists(os.path.join(d, "SOUL.md")): fail(f"{rel(d)}: SOUL.md missing")
    else:
        n = sum(1 for _ in open(os.path.join(d, "SOUL.md"), encoding="utf-8"))
        if n > 40: fail(f"{rel(d)}/SOUL.md: {n} lines, limit is 40")
    if not os.path.exists(os.path.join(d, "CARD.md")): fail(f"{rel(d)}: CARD.md missing")
    return name, " ".join(goal_lines).strip(), f.get("tools", "")

def main():
    if "--charter" in sys.argv:
        paths = [a for a in sys.argv[sys.argv.index("--charter") + 1:] if not a.startswith("--")]
        bad = 0
        for p in paths:
            before = len(fails)
            f, _ = fm_and_body(p); star = f.get("name", "x").split("-")[0]
            check_charter(p, star, standalone=True)
            new = fails[before:]
            if new:
                bad += 1; print(f"FAIL {p}")
                for m in new: print("  - " + m.split(": ", 1)[-1])
            else: print(f"PASS {p}")
        print(f"\n{len(paths) - bad} passed, {bad} failed"); return 1 if bad else 0
    kit = json.load(open(os.path.join(ROOT, "kit.json")))
    if not os.path.exists(os.path.join(ROOT, kit["guide"], "SKILL.md")): fail("kit.json: guide path has no SKILL.md")
    else: check_skill_frontmatter(os.path.join(ROOT, kit["guide"], "SKILL.md"), False)
    charters = {}
    for s in kit["stars"]:
        p = os.path.join(ROOT, s["path"])
        if not os.path.isdir(p): fail(f"kit.json: {s['path']} missing"); continue
        if os.path.exists(os.path.join(p, "SKILL.md")):
            name, goal, tools = check_charter(os.path.join(p, "SKILL.md"), s["star"])
            if name != s["id"]: fail(f"kit.json: id {s['id']} != charter name {name}")
            charters[name] = (goal, tools)
        for sk in s["skills"]:
            skp = os.path.join(p, sk, "SKILL.md")
            if not os.path.exists(skp): fail(f"kit.json: {s['path']}/{sk}/SKILL.md missing"); continue
            check_skill_frontmatter(skp, True)
    # charters on disk that kit.json forgot
    for p in glob.glob(os.path.join(ROOT, ".agents", "*", "SKILL.md")):
        star = os.path.basename(os.path.dirname(p))
        if star != "guide" and not any(s["star"] == star for s in kit["stars"]): fail(f"{rel(p)}: charter exists but kit.json does not list {star}")

    # the map: kit.json is the one source
    ids = {s["id"]: s for s in kit["stars"]}
    for s in kit["stars"]:
        for t in s["hands_to"]:
            if t in ids and s["id"] not in ids[t]["receives_from"]: fail(f"map: {s['id']} hands to {t}, but {t} does not list it in receives_from")
            if t not in ids and t not in ("owner",): fail(f"map: {s['id']} hands to unknown {t}")
        for r in s["receives_from"]:
            if r in ids and s["id"] not in ids[r]["hands_to"]: fail(f"map: {s['id']} receives from {r}, but {r} does not hand to it")
            if r not in ids and r not in ("owner", "schedule"): fail(f"map: {s['id']} receives from unknown {r}")
        cp = os.path.join(ROOT, s["path"], "SKILL.md")
        if os.path.exists(cp):
            f, body = fm_and_body(cp)
            ctools = [t.strip() for t in f.get("tools", "").split(",") if t.strip()]
            if sorted(ctools) != sorted(s["tools"]): fail(f"map: {s['id']} charter tools {ctools} != kit.json {s['tools']}")
            hand = sections(body).get("6. Handoffs", "").lower()
            for t in s["hands_to"]:
                if t in ids and ids[t]["star"] not in hand: fail(f"map: {rel(cp)} Handoffs part does not name {ids[t]['star'].capitalize()}")
        card = os.path.join(ROOT, s["path"], "CARD.md")
        if s["tier"] == "ascension" and os.path.exists(card) and "ascension" not in open(card, encoding="utf-8").read().lower():
            fail(f"map: {rel(card)} does not say the star ships in Ascension")
    bv = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "build_vault.py"), "--check"], capture_output=True, text=True)
    if bv.returncode: fail("map: " + bv.stdout.strip().replace("FAIL ", ""))
    # registry
    reg = os.path.join(ROOT, "newsroom", "governance", "registry.json")
    if os.path.exists(reg):
        rows = {d["id"]: d for d in json.load(open(reg))["desks"]}
        for name, (goal, tools) in charters.items():
            if name not in rows: fail(f"registry: no row for {name}"); continue
            if rows[name]["goal"].strip() != goal: fail(f"registry: goal for {name} differs from the charter")
            extra = [t.strip() for t in tools.split(",") if t.strip() and t.strip() not in rows[name]["tools"]]
            if extra: fail(f"registry: {name} charter lists tools not in registry: {', '.join(extra)}")
        for rid in rows:
            if rid not in charters: fail(f"registry: row {rid} has no charter")
    # plugin manifests and the tool list
    version = open(os.path.join(ROOT, "VERSION")).read().strip()
    for mf in ["plugin.json", "marketplace.json"]:
        mp = os.path.join(ROOT, ".claude-plugin", mf)
        if not os.path.exists(mp): fail(f".claude-plugin/{mf} missing"); continue
        try: m = json.load(open(mp))
        except Exception as e: fail(f".claude-plugin/{mf}: {e}"); continue
        if mf == "plugin.json":
            if m.get("version") != version: fail(f".claude-plugin/plugin.json version {m.get('version')} != VERSION {version}")
            for key in ["skills", "agents"]:
                for pth in m.get(key, []):
                    if not os.path.exists(os.path.join(ROOT, pth)): fail(f".claude-plugin/plugin.json {key}: {pth} does not exist")
        else:
            for pl in m.get("plugins", []):
                if pl.get("version") != version: fail(f".claude-plugin/marketplace.json plugin {pl.get('name')} version != VERSION")
                if not os.path.isdir(os.path.join(ROOT, pl.get("source", "nope"))): fail(f".claude-plugin/marketplace.json source {pl.get('source')} is not a folder")
    readme = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
    for tool in kit.get("tools", []):
        if f"| {tool['label']} |" not in readme: fail(f"README: no install table row for {tool['label']}")
        page = os.path.join(ROOT, tool.get("page", "integrations/" + tool["key"]), "README.md")
        if not os.path.exists(page): fail(f"integrations: no page for {tool['label']} ({rel(page)})")
        if not (TOOLS_JS := open(os.path.join(ROOT, "scripts", "install.js")).read()) or f"  {tool['key']}:" not in TOOLS_JS: fail(f"install.js: no TOOLS entry for {tool['key']}")
    # evals recorded since the last charter change
    latest = os.path.join(ROOT, "evals", "results", "latest.json")
    if os.path.exists(latest):
        import importlib.util
        spec = importlib.util.spec_from_file_location("kit_eval", os.path.join(ROOT, "scripts", "eval.py"))
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        rec = json.load(open(latest))
        if rec.get("charters_hash") != mod.charters_hash():
            fail(f"evals: charters, registry, or eval specs changed since evals/results/latest.json was recorded ({rec.get('recorded_at')}). Run: python3 scripts/eval.py --record")
        failed = [r["desk"] for r in rec.get("results", []) if not r.get("pass")]
        if failed: fail(f"evals: last recorded run failed for {', '.join(failed)}")
    # the vault as a product: Obsidian config, the canvas, the dashboard
    for jf in glob.glob(os.path.join(ROOT, "newsroom", ".obsidian", "*.json")):
        try: json.load(open(jf))
        except Exception as e: fail(f"{rel(jf)}: {e}")
    canvas = os.path.join(ROOT, "newsroom", "Constellation.canvas")
    if os.path.exists(canvas) and os.path.exists(reg):
        try:
            c = json.load(open(canvas)); ids = {n.get("id") for n in c.get("nodes", [])}
            for rid in rows:
                if rid not in ids: fail(f"Constellation.canvas: no node for {rid}")
            if "owner" not in ids: fail("Constellation.canvas: no owner node")
        except Exception as e: fail(f"Constellation.canvas: {e}")
    dash = os.path.join(ROOT, "scripts", "dashboard")
    if os.path.isdir(dash):
        import ast, importlib.util as ilu
        for py in glob.glob(os.path.join(dash, "*.py")):
            try: ast.parse(open(py, encoding="utf-8").read())
            except SyntaxError as e: fail(f"{rel(py)}: {e}")
        vd = os.path.join(dash, "vaultdata.py")
        if os.path.exists(vd):
            try:
                spec = ilu.spec_from_file_location("vaultdata", vd); m = ilu.module_from_spec(spec); spec.loader.exec_module(m)
                if "streamlit" in sys.modules and not os.environ.get("KIT_ALLOW_STREAMLIT"): fail("scripts/dashboard/vaultdata.py imports streamlit; it must stay standard library")
            except Exception as e: fail(f"scripts/dashboard/vaultdata.py does not import without Streamlit: {e}")
    # words that never ship: the owner's private dashboard title, and em dashes in prose
    try:
        tracked = subprocess.run(["git", "ls-files", "-co", "--exclude-standard"], cwd=ROOT, capture_output=True, text=True).stdout.split()
    except Exception:
        tracked = []
    for f in tracked:
        p = os.path.join(ROOT, f)
        if not os.path.isfile(p) or "/node_modules/" in p or f.endswith((".png", ".pdf", ".pptx", ".jpg")): continue
        try: text = open(p, encoding="utf-8").read()
        except Exception: continue
        if PRIVATE.search(text): fail(f"{f}: carries a private title that never ships")
        if f != "CHANGELOG.md" and not (f.startswith("evals/") and "/input/" in f):
            if PRICE in text or STORE in text: fail(f"{f}: carries a price or the old store link")
        if f.endswith(".md") and not ("evals/" in f and "/input/" in f) and "fixtures/" not in f and f != "CHANGELOG.md":
            for m in PRONOUN.finditer(re.sub(r"`[^`]*`", "", text)):
                line = text.count("\n", 0, m.start()) + 1
                fail(f"{f}:{line}: pronoun '{m.group(0)}'; call a star by name or 'it', the owner 'you' or 'the owner'"); break
        if f.endswith(".md") and "\u2014" in text and not (f.startswith("evals/") and "/input/" in f) and "fixtures/" not in f:
            fail(f"{f}: em dash in prose")
    # duplicates
    try:
        files = subprocess.run(["git", "ls-files", "-co", "--exclude-standard", "*.md"], cwd=ROOT, capture_output=True, text=True).stdout.split()
    except Exception:
        files = [rel(p) for p in glob.glob(os.path.join(ROOT, "**", "*.md"), recursive=True)]
    seen = {}
    for f in files:
        p = os.path.join(ROOT, f)
        if not os.path.exists(p) or "/node_modules/" in p or f.startswith("evals/") and "/input/" in f: continue  # eval fixtures may repeat on purpose
        h = hashlib.sha256(open(p, "rb").read()).hexdigest()
        if h in seen: fail(f"duplicate content: {f} == {seen[h]}")
        else: seen[h] = f
    if fails:
        for m in fails: print("FAIL " + m)
        print(f"\n{len(fails)} problem(s)"); return 1
    print(f"OK  {len(charters)} charter(s), {sum(len(s['skills']) for s in kit['stars'])} working skill(s), guide, {len(seen)} markdown files, no duplicates")
    return 0

if __name__ == "__main__":
    sys.exit(main())
