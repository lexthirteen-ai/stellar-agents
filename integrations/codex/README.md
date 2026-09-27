# Codex

## Install

From the folder that holds the unzipped release:

```bash
npx skills add ./stellar-agents --agent codex
```

That is the skills CLI Codex users already use, pointed at a local folder, and `--global` puts the skills in your home folder. Or the kit's own installer:

```bash
node scripts/install.js --tools codex
```

Add `--project` to install into the current repo's `.agents/skills/` instead of your home folder.

## Where files land

Every star, working skill, and the guide go to `~/.agents/skills/<name>/`. Codex reads that folder for personal skills, and `.agents/skills/` in a repo for project skills.

## Activate a star

Codex loads a skill when the task matches its description. To keep one always on, add a line to your `AGENTS.md`:

```
Use the constellation skills in ~/.agents/skills for reporting, drafting, and checking. Nothing is sent without a human.
```

The installer never edits `AGENTS.md` for you. It prints that line and leaves the choice with you.

The plugin and the skills CLI bring the stars and their working skills. The vault, the runner, the hooks, and the evals come only from `node scripts/install.js --vault <dir>` in the unzipped release. See [docs/runtime.md](../../docs/runtime.md).

Back to the [main README](../../README.md).
