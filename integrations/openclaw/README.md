# OpenClaw

## Install

Move into the unzipped folder first (`cd ~/Downloads/stellar-agents`, the same name every release), then one star at a time with OpenClaw's own command:

```bash
openclaw skills install ./.agents/<star> --as <id>
```

Or the skills CLI from the same folder, `npx skills add . --agent openclaw`, or the kit's own installer:

```bash
node ~/Downloads/stellar-agents/scripts/install.js --tools openclaw
```

## Where files land

Every star, working skill, and the guide go to `~/.agents/skills/<name>/`, which OpenClaw reads as personal agent skills. `openclaw skills install` with a workspace flag puts one star into that workspace instead.

## Personas

OpenClaw gives each agent a `SOUL.md` in its workspace. Each star ships its own inside its skill folder. To run a star as its own OpenClaw agent, copy `.agents/<star>/SOUL.md` into that agent's workspace as `SOUL.md`. The charter's never list still applies. Persona is voice, not authority.

The plugin and the skills CLI bring the stars and their working skills. The vault, the runner, the hooks, and the evals come only from `node ~/Downloads/stellar-agents/scripts/install.js --vault <dir>` in the unzipped release. See [docs/runtime.md](../../docs/runtime.md).

Back to the [main README](../../README.md).
