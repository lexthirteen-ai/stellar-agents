# Gemini CLI

## Install

Gemini CLI installs a skill from a local folder. Move into the unzipped folder first (it is always called `stellar-agents`), then one star at a time:

```bash
cd ~/Downloads/stellar-agents
gemini skills install ./.agents/aurora --consent
```

Or the kit's own installer, which writes every star and skill into this tool's folder in one go with `node ~/Downloads/stellar-agents/scripts/install.js --tools gemini`.

## Where files land

Gemini CLI reads `~/.gemini/skills/<name>/` and `~/.agents/skills/<name>/` at user level, and `.gemini/skills/` or `.agents/skills/` in a workspace. The kit's installer writes `~/.gemini/skills/<name>/`.

## Activate a star

Gemini activates a skill through its `activate_skill` tool when a task matches, after a confirmation prompt that names the skill and its folder. Say yes, and the charter is in context.

The plugin and the skills CLI bring the stars and their working skills. The vault, the runner, the hooks, and the evals come only from `node ~/Downloads/stellar-agents/scripts/install.js --vault <dir>` in the unzipped release. See [docs/runtime.md](../../docs/runtime.md).

Back to the [main README](../../README.md).
