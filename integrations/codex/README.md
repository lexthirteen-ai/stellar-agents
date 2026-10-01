# Codex

## Install

Double-click the zip. It unzips to a folder called `stellar-agents`, the same name every release. Then, from any Terminal window:

```bash
node ~/Downloads/stellar-agents/scripts/install.js --tools codex --vault ~/stellar
```

That writes every star to `~/.agents/skills/` for Codex and builds the vault with the runner, which the skills CLI cannot do. To run a star through Codex, from any folder: `python3 ~/stellar/scripts/newsroom.py run draco-chief-of-staff --backend codex --trigger owner --task "Write today's brief."`

If you only want the skills, the skills CLI Codex users already know reads the folder you are in, with `--global` for your home folder:

```bash
cd ~/Downloads/stellar-agents
npx skills add . --agent codex
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

The plugin and the skills CLI bring the stars and their working skills. The vault, the runner, the hooks, and the evals come only from `node ~/Downloads/stellar-agents/scripts/install.js --vault <dir>` in the unzipped release. See [docs/runtime.md](../../docs/runtime.md).

Back to the [main README](../../README.md).
