#!/usr/bin/env node
// Stellar Agents installer. Zero dependencies. Node 16.7 or later.
// Reads kit.json, then copies each star, its skills, and the guide into the folders each tool reads from.
// The repo layout is for humans. This script produces the shapes tools expect, at install time.
// It never edits a file it did not create, and never overwrites without --force.
"use strict";
const fs = require("fs"), os = require("os"), path = require("path"), readline = require("readline");

const ROOT = path.resolve(__dirname, "..");
const KIT = JSON.parse(fs.readFileSync(path.join(ROOT, "kit.json"), "utf8"));
const HOME = process.env.HOME || os.homedir();
const GROUP = KIT.group || "constellation";

const XDG = process.env.XDG_CONFIG_HOME || path.join(HOME, ".config");
// One row per tool that reads the Agent Skills format. detect is the folder that says the tool is installed.
// Codex, Gemini CLI, and OpenClaw read ~/.agents/skills as a shared location; the installer writes it once and says so.
const TOOLS = {
  claude:   { label: "Claude Code", detect: ".claude",           skills: (h) => path.join(h, ".claude", "skills"), agents: (h) => path.join(h, ".claude", "agents") },
  codex:    { label: "Codex",       detect: ".codex",            skills: (h) => path.join(h, ".agents", "skills") },
  gemini:   { label: "Gemini CLI",  detect: ".gemini",           skills: (h) => path.join(h, ".gemini", "skills") },
  openclaw: { label: "OpenClaw",    detect: ".openclaw",         skills: (h) => path.join(h, ".agents", "skills") },
  hermes:   { label: "Hermes",      detect: ".hermes",           skills: (h) => path.join(h, ".hermes", "skills", GROUP) },
  agents:   { label: "Any tool that reads ~/.agents/skills", detect: null, skills: (h) => path.join(h, ".agents", "skills") },
};
const ALL = Object.keys(TOOLS).filter((k) => k !== "agents");

const args = process.argv.slice(2);
const flag = (n) => args.includes(`--${n}`);
const val = (n) => { const i = args.indexOf(`--${n}`); return i >= 0 && args[i + 1] && !args[i + 1].startsWith("--") ? args[i + 1] : null; };

if (flag("help") || flag("h")) {
  console.log(`
${KIT.name} v${KIT.version}

  node scripts/install.js [options]            from the unzipped release folder

  --tools claude,codex,gemini,openclaw,hermes,all
                                             which tools to install into (asks if omitted)
  --tools agents                             only the shared ~/.agents/skills folder, which Codex,
                                             Gemini CLI, and OpenClaw all read
  --stars carina,aurora,...                  only these stars (default: every star in kit.json)
  --project                                  install into ./.agents/skills and ./.claude in the current folder
  --vault <dir>                              create or upgrade a vault at <dir>: the stars as project agents, hooks, runner,
                                             dashboard, Obsidian config. Safe over an existing vault: files you edited are
                                             kept and the new version lands beside them; your own files are never written.
  --pack tool-scout,publish-weekly           add an optional pack (with --vault, its stars join the registry)
  --dry-run                                  print what would be written, write nothing
  --force                                    replace folders and files that already exist
  --yes                                      no questions, use detected tools
  --list                                     print what this kit contains

  Claude Code   ~/.claude/skills/<name>/  and  ~/.claude/agents/<name>.md
  Codex         ~/.agents/skills/<name>/
  Gemini CLI    ~/.gemini/skills/<name>/
  OpenClaw      ~/.agents/skills/<name>/  (persona in each star's SOUL.md)
  Hermes        ~/.hermes/skills/${GROUP}/<name>/

  Claude Code also installs as a plugin: /plugin marketplace add ./stellar-agents
  Any of 100+ tools: npx skills add ./stellar-agents
`); process.exit(0);
}

function frontmatter(file) {
  const text = fs.readFileSync(file, "utf8");
  if (!text.startsWith("---\n")) throw new Error(`${file}: no frontmatter`);
  const end = text.indexOf("\n---", 4);
  const fm = text.slice(4, end), body = text.slice(end + 4).replace(/^\n+/, "");
  const get = (k) => { const m = fm.match(new RegExp(`^${k}:\\s*(.*)$`, "m")); return m ? m[1].trim() : ""; };
  const meta = (k) => { const m = fm.match(new RegExp(`^  ${k}:\\s*"?(.*?)"?\\s*$`, "m")); return m ? m[1].trim() : ""; };
  return { name: get("name"), description: get("description"), tools: get("tools") || meta("tools"), body };
}

const stars = KIT.stars || [];
if (flag("list")) {
  console.log(`${KIT.name} v${KIT.version}`);
  console.log(`  guide  ${frontmatter(path.join(ROOT, KIT.guide, "SKILL.md")).name}`);
  for (const s of stars) {
    console.log(`  star   ${s.id.padEnd(26)} ${s.star}${s.skills.length ? "  skills: " + s.skills.join(", ") : ""}`);
  }
  process.exit(0);
}

const dry = flag("dry-run"), force = flag("force"), yes = flag("yes"), project = flag("project");
const starFilter = val("stars") ? val("stars").split(",").map((s) => s.trim().toLowerCase()).filter(Boolean) : null;
const wanted = stars.filter((s) => !starFilter || starFilter.includes(s.star) || starFilter.includes(s.id));
const installGuide = !starFilter || starFilter.includes("guide");

async function chooseTools() {
  const fromFlag = val("tools");
  const parse = (str) => { const l = str.split(",").map((s) => s.trim().toLowerCase()).filter(Boolean); if (l.includes("all")) return ALL; const bad = l.filter((t) => !TOOLS[t]); if (bad.length) { console.error(`Unknown tool: ${bad.join(", ")}. Known: ${Object.keys(TOOLS).join(", ")}`); process.exit(2); } return l; };
  if (fromFlag) return parse(fromFlag);
  const detected = ALL.filter((k) => TOOLS[k].detect && fs.existsSync(path.join(HOME, TOOLS[k].detect)));
  if (yes) return detected;
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  const ask = (q) => new Promise((res) => rl.question(q, res));
  console.log(`\n${KIT.name} v${KIT.version}`);
  console.log(detected.length ? `Found: ${detected.map((t) => TOOLS[t].label).join(", ")}` : "No tool folders found in your home directory.");
  const ans = await ask(`Install into which tools? [${ALL.join(", ")}, agents, all] (${detected.join(",") || "claude"}): `);
  rl.close();
  return parse(ans.trim() || detected.join(",") || "claude");
}

const log = [];
function note(kind, dest) { log.push(`${kind.padEnd(7)} ${dest}`); }
function guard(dest) { if (fs.existsSync(dest) && !force) { note("skip", `${dest}  (exists, use --force)`); return false; } note(dry ? "would" : "write", dest); return !dry; }
function writeFile(dest, content) { if (!guard(dest)) return; fs.mkdirSync(path.dirname(dest), { recursive: true }); fs.writeFileSync(dest, content); }
function copyFile(src, dest) { if (!guard(dest)) return; fs.mkdirSync(path.dirname(dest), { recursive: true }); fs.copyFileSync(src, dest); }
function copyFolderFilesOnly(src, dest) {
  if (!guard(dest + "/")) return;
  fs.rmSync(dest, { recursive: true, force: true }); fs.mkdirSync(dest, { recursive: true });
  for (const f of fs.readdirSync(src)) { const p = path.join(src, f); if (fs.statSync(p).isFile()) fs.copyFileSync(p, path.join(dest, f)); }
}
function copyTree(src, dest) { if (!guard(dest + "/")) return; fs.rmSync(dest, { recursive: true, force: true }); fs.mkdirSync(path.dirname(dest), { recursive: true }); fs.cpSync(src, dest, { recursive: true, filter: (p) => !/(^|[\\/])(__pycache__|node_modules|\.DS_Store)$/.test(p) }); }

function agentFile(skillMd) {
  const f = frontmatter(skillMd);
  return `---\nname: ${f.name}\ndescription: ${f.description}\ntools: ${f.tools || "Read"}\n---\n\n${f.body}`;
}

function installInto(skillsDir, agentsDir) {
  const done = new Set();
  const once = (dest, fn) => { if (done.has(dest)) return; done.add(dest); fn(); };
  if (installGuide) {
    const g = path.join(ROOT, KIT.guide); const name = frontmatter(path.join(g, "SKILL.md")).name;
    const dest = path.join(skillsDir, name);
    once(dest, () => {
      copyTree(g, dest);
      if (dry || !fs.existsSync(dest)) return;
      const refs = path.join(dest, "references"); fs.mkdirSync(refs, { recursive: true });
      for (const t of fs.readdirSync(path.join(ROOT, "templates"))) fs.copyFileSync(path.join(ROOT, "templates", t), path.join(refs, t));
      const aurora = stars.find((s) => s.star === "aurora");
      if (aurora && fs.existsSync(path.join(ROOT, aurora.path, "SKILL.md"))) fs.copyFileSync(path.join(ROOT, aurora.path, "SKILL.md"), path.join(refs, `${aurora.id}.md`));
    });
  }
  for (const s of wanted) {
    const src = path.join(ROOT, s.path); const skillMd = path.join(src, "SKILL.md");
    if (!fs.existsSync(skillMd)) { note("none", `${s.id}  (card only in this tier)`); continue; }
    once(path.join(skillsDir, s.id), () => copyFolderFilesOnly(src, path.join(skillsDir, s.id)));
    if (agentsDir) writeFile(path.join(agentsDir, `${s.id}.md`), agentFile(skillMd));
    for (const sk of s.skills) once(path.join(skillsDir, sk), () => copyTree(path.join(src, sk), path.join(skillsDir, sk)));
  }
}


// ---------- the vault, with a manifest so an upgrade never disrupts ----------
// Every file the installer writes into a vault is recorded in .stellar/manifest.json with its hash.
// On the next install, over the same folder:
//   a file the installer wrote and nobody touched is replaced;
//   a file the owner edited is kept, and the new version lands beside it as <file>.<suffix>;
//   owner data (kit.json owner_files) is never written once it exists;
//   registry rows for new stars are added, Thuban's active, every other new star proposed until the owner ticks.
const crypto = require("crypto");
const sha = (buf) => crypto.createHash("sha256").update(buf).digest("hex");
const SUFFIX = KIT.upgrade_suffix || "new";
const OWNER = (KIT.owner_files || []).map((f) => f.replace(/\\/g, "/"));
const VAULT_DIRS = ["Daily", "Templates", "inputs/inbox", "inputs/calendar", "feedback", "governance/proposals", "governance/runs",
  "outputs/plan", "outputs/schedule", "outputs/signals", "outputs/drafts", "outputs/staged", "outputs/rejected", "outputs/carried",
  "outputs/review", "outputs/catalog", "outputs/audit", "outputs/pipeline", "outputs/money"];
const packs = (val("pack") || "").split(",").map((p) => p.trim()).filter(Boolean);
for (const p of packs) if (!(KIT.packs || []).some((k) => k.name === p)) { console.error(`Unknown pack: ${p}. Known: ${(KIT.packs || []).map((k) => k.name).join(", ")}`); process.exit(2); }

function isOwnerData(rel) {
  if (rel === "governance/registry.json" || rel === "governance/audit-log.md") return false; // merged and appended below, never replaced
  return OWNER.some((o) => (o.endsWith("/") ? rel.startsWith(o) : rel === o)) && !/(^|\/)README\.md$/.test(rel) && !rel.startsWith("governance/proposals/TEMPLATE");
}

function vaultPlan(dir) {
  // [relative destination, Buffer content] for everything the kit puts in a vault
  const out = [];
  const walk = (src, prefix) => {
    if (!fs.existsSync(src)) return;
    for (const f of fs.readdirSync(src)) {
      if (/^(__pycache__|node_modules|\.DS_Store)$/.test(f)) continue;
      const p = path.join(src, f), rel = prefix ? `${prefix}/${f}` : f;
      if (fs.statSync(p).isDirectory()) walk(p, rel); else out.push([rel, fs.readFileSync(p)]);
    }
  };
  walk(path.join(ROOT, "newsroom"), "");
  out.push(["HOUSE-STYLE.md", fs.readFileSync(path.join(ROOT, "templates", "HOUSE-STYLE.md"))]);
  for (const f of ["newsroom.py", "copydesk.py", "check.py", "eval.py", "build_vault.py"]) if (fs.existsSync(path.join(ROOT, "scripts", f))) out.push([`scripts/${f}`, fs.readFileSync(path.join(ROOT, "scripts", f))]);
  walk(path.join(ROOT, "scripts", "hooks"), "scripts/hooks");
  walk(path.join(ROOT, "scripts", "dashboard"), "scripts/dashboard");
  const skill = (src, destName) => { walk(src, `.claude/skills/${destName}`); };
  for (const s of wanted) {
    const src = path.join(ROOT, s.path), md = path.join(src, "SKILL.md");
    if (!fs.existsSync(md)) continue;
    for (const f of fs.readdirSync(src)) if (fs.statSync(path.join(src, f)).isFile()) out.push([`.claude/skills/${s.id}/${f}`, fs.readFileSync(path.join(src, f))]);
    out.push([`.claude/agents/${s.id}.md`, Buffer.from(agentFile(md))]);
    for (const sk of s.skills) if (fs.existsSync(path.join(src, sk))) skill(path.join(src, sk), sk);
  }
  if (installGuide) { const g = path.join(ROOT, KIT.guide); skill(g, frontmatter(path.join(g, "SKILL.md")).name); }
  return out.filter(([rel]) => rel !== "governance/registry.json" && rel !== "governance/audit-log.md");
}

function installVault(dir) {
  const mpath = path.join(dir, ".stellar", "manifest.json");
  const manifest = fs.existsSync(mpath) ? JSON.parse(fs.readFileSync(mpath, "utf8")) : { files: {} };
  const upgrade = { from: manifest.kit ? `${manifest.kit} ${manifest.version}` : null, to: `${KIT.name} ${KIT.version}`, kept: [], replaced: [], added: [], added_stars: [] };
  const files = {};
  for (const [rel, buf] of vaultPlan(dir)) {
    const dest = path.join(dir, rel), h = sha(buf);
    if (!fs.existsSync(dest)) { note(dry ? "would" : "write", rel); if (!dry) { fs.mkdirSync(path.dirname(dest), { recursive: true }); fs.writeFileSync(dest, buf); } files[rel] = h; upgrade.added.push(rel); continue; }
    const cur = sha(fs.readFileSync(dest));
    if (cur === h) { files[rel] = h; continue; }
    if (isOwnerData(rel)) { note("keep", `${rel}  (yours, never written)`); continue; }
    if (manifest.files[rel] && manifest.files[rel] === cur) {
      note(dry ? "would" : "replace", rel); if (!dry) fs.writeFileSync(dest, buf); files[rel] = h; upgrade.replaced.push(rel); continue;
    }
    note("keep", `${rel}  (you edited it; the new version is ${rel}.${SUFFIX})`);
    if (!dry) fs.writeFileSync(`${dest}.${SUFFIX}`, buf);
    if (manifest.files[rel]) files[rel] = manifest.files[rel];
    upgrade.kept.push(rel);
  }
  if (!dry) for (const d of VAULT_DIRS) fs.mkdirSync(path.join(dir, d), { recursive: true });
  // The registry: new rows are added, existing rows are never touched.
  const rpath = path.join(dir, "governance", "registry.json");
  const kitReg = JSON.parse(fs.readFileSync(path.join(ROOT, "newsroom", "governance", "registry.json"), "utf8"));
  const reg = fs.existsSync(rpath) ? JSON.parse(fs.readFileSync(rpath, "utf8")) : { $schema_note: kitReg.$schema_note, desks: [] };
  const fresh = reg.desks.length === 0;
  const packRows = [];
  for (const p of packs) { const pr = path.join(ROOT, KIT.packs.find((k) => k.name === p).path, "registry.json"); if (fs.existsSync(pr)) packRows.push(...JSON.parse(fs.readFileSync(pr, "utf8")).desks); }
  const wantedIds = new Set(wanted.map((s) => s.id));
  for (const row of [...kitReg.desks.filter((r) => wantedIds.has(r.id)), ...packRows]) {
    if (reg.desks.some((d) => d.id === row.id)) continue;
    const r = { ...row };
    if (!fresh && !row.id.startsWith("thuban-")) r.status = "proposed";
    reg.desks.push(r); upgrade.added_stars.push(r.id); note(dry ? "would" : "add", `registry row ${r.id} (${r.status})`);
  }
  // The audit log: created once, then one INSTALLED line per install, appended.
  const apath = path.join(dir, "governance", "audit-log.md");
  const stamp = new Date().toISOString().slice(0, 16).replace("T", " ");
  const line = `${stamp} | INSTALLED | installer | ${upgrade.to}${upgrade.from ? ` over ${upgrade.from}` : ""}, added ${upgrade.added_stars.length} star(s), kept ${upgrade.kept.length} edited file(s)\n`;
  if (!dry) {
    fs.mkdirSync(path.dirname(rpath), { recursive: true });
    fs.writeFileSync(rpath, JSON.stringify(reg, null, 2) + "\n");
    if (!fs.existsSync(apath)) fs.copyFileSync(path.join(ROOT, "newsroom", "governance", "audit-log.md"), apath);
    let log = fs.readFileSync(apath, "utf8");
    log = log.trimEnd().endsWith("```") ? log.trimEnd().slice(0, -3).trimEnd() + "\n" + line + "```\n" : log.replace(/\n*$/, "\n") + line;
    fs.writeFileSync(apath, log);
    fs.mkdirSync(path.dirname(mpath), { recursive: true });
    fs.writeFileSync(mpath, JSON.stringify({ kit: KIT.name, version: KIT.version, installed_at: new Date().toISOString(), files }, null, 2) + "\n");
    if (upgrade.from) fs.writeFileSync(path.join(dir, ".stellar", "upgrade.json"), JSON.stringify(upgrade, null, 2) + "\n");
  }
  if (upgrade.from) note("note", `upgrade from ${upgrade.from}: ${upgrade.replaced.length} replaced, ${upgrade.kept.length} kept, ${upgrade.added_stars.length} star(s) added. Thuban's next run is intake.`);
}

function installPack(name, tools, base) {
  const pack = KIT.packs.find((k) => k.name === name), root = path.join(ROOT, pack.path);
  const targets = [];
  const vault = val("vault");
  if (vault) targets.push([path.join(path.resolve(vault), ".claude", "skills"), path.join(path.resolve(vault), ".claude", "agents")]);
  for (const t of tools) { const tool = TOOLS[t]; targets.push([project ? path.join(base, t === "claude" ? ".claude/skills" : ".agents/skills") : tool.skills(base), tool.agents ? (project ? path.join(base, ".claude", "agents") : tool.agents(base)) : null]); }
  const starsDir = path.join(root, ".agents");
  for (const [skillsDir, agentsDir] of targets) {
    for (const star of fs.existsSync(starsDir) ? fs.readdirSync(starsDir) : []) {
      const sdir = path.join(starsDir, star), md = path.join(sdir, "SKILL.md");
      for (const f of fs.readdirSync(sdir)) {
        const p = path.join(sdir, f);
        if (fs.statSync(p).isDirectory()) copyTree(p, path.join(skillsDir, f));
      }
      if (fs.existsSync(md)) {
        const id = frontmatter(md).name;
        copyFolderFilesOnly(sdir, path.join(skillsDir, id));
        if (agentsDir) writeFile(path.join(agentsDir, `${id}.md`), agentFile(md));
      }
    }
  }
}

(async () => {
  const vault = val("vault");
  const tools = await chooseTools();
  if (!tools.length && !vault && !packs.length) { console.log("Nothing to install into. Pass --tools claude,codex,openclaw,hermes or --tools all."); process.exit(0); }
  const base = project ? process.cwd() : HOME;
  const seenSkillDirs = new Set();
  for (const t of tools) {
    const tool = TOOLS[t];
    const skillsDir = project ? (t === "claude" ? path.join(base, ".claude", "skills") : path.join(base, ".agents", "skills")) : tool.skills(base);
    const agentsDir = tool.agents ? (project ? path.join(base, ".claude", "agents") : tool.agents(base)) : null;
    if (seenSkillDirs.has(skillsDir) && !agentsDir) { note("same", `${tool.label} reads ${skillsDir}, already written`); continue; }
    seenSkillDirs.add(skillsDir);
    installInto(skillsDir, agentsDir);
  }
  if (vault) installVault(path.resolve(vault));
  for (const name of packs) installPack(name, tools, project ? process.cwd() : HOME);
  console.log(`\n${KIT.name} v${KIT.version}${dry ? "  [dry run]" : ""}\n`);
  for (const l of log) console.log("  " + l);
  const n = (k) => log.filter((l) => l.startsWith(k)).length;
  console.log(`\n  ${dry ? "would write" : "wrote"} ${n("write") + n("would")}, skipped ${n("skip")}`);
  if (tools.includes("codex")) console.log(`\nCodex loads skills on demand. To keep a star always on, add one line to AGENTS.md, for example:\n  Use the ${GROUP} skills in ~/.agents/skills for reporting, drafting, and checking. Nothing is sent without a human.`);
  if (tools.includes("openclaw")) console.log(`\nOpenClaw: each star's persona is its SOUL.md. To run a star as its own agent, copy that file into the agent's workspace as SOUL.md.`);
  if (vault) console.log(`\nVault at ${path.resolve(vault)}. Open it in Obsidian, fill in HOUSE-STYLE.md, then: cd ${path.resolve(vault)} && python3 scripts/newsroom.py status\nThe dashboard needs one install: pip install -r scripts/dashboard/requirements.txt, then python3 scripts/newsroom.py dashboard`);
  console.log(`\nNothing here sends, spends, publishes, or schedules. That step stays with you.\n`);
})().catch((e) => { console.error(e.message || e); process.exit(1); });
