# Claude Code

## Install

Start Claude Code inside the unzipped release folder (its name carries the version, for example `cd ~/Downloads/stellar-agents-v0.1.1`), then:

```
/plugin marketplace add .
/plugin install constellation@stellar-agents
```

That loads every star as a skill and as a subagent, namespaced `constellation:<name>`, with each star's working skills beside them. When a new release lands, unzip it over the same folder and run `/plugin update`. Or from a terminal, the kit's own installer:

```bash
node scripts/install.js --tools claude
```

Add `--project` to install into the current repo's `.claude/` instead of your home folder.

## Where files land

| What | Where |
|---|---|
| Each star and each working skill | `~/.claude/skills/<name>/` |
| Each star as a subagent | `~/.claude/agents/<name>.md`, with its `tools` list lifted from the charter |
| The guide | `~/.claude/skills/constellation-guide/`, with the templates copied into `references/` |

## Activate a star

Skills load when a task matches their description. To call a star as a subagent, name it: "Use the aurora-reporter agent on the export in inputs/feeds/." The star's persona is in its skill folder's `SOUL.md` and summarized in the Voice block of the agent file.

## Manual copy

Copy `.agents/<star>/` (the files, not the skill subfolders) to `~/.claude/skills/<id>/`, and each `.agents/<star>/<skill>/` to `~/.claude/skills/<skill>/`. For the subagent file, copy `SKILL.md` to `~/.claude/agents/<id>.md` and keep its `tools:` line.

The plugin and the skills CLI bring the stars and their working skills. The vault, the runner, the hooks, and the evals come only from `node scripts/install.js --vault <dir>` in the unzipped release. See [docs/runtime.md](../../docs/runtime.md).

Back to the [main README](../../README.md).
