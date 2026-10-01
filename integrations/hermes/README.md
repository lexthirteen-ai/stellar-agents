# Hermes

## Install

From any Terminal window:

```bash
node ~/Downloads/stellar-agents/scripts/install.js --tools hermes
```

## Where files land

Hermes groups skills in subfolders, so everything lands under `~/.hermes/skills/constellation/<name>/`.

## Install one star by hand

Hermes reads a skill folder that holds a `SKILL.md`. Copy `.agents/<star>/` to `~/.hermes/skills/constellation/<id>/`, where the id is the `name:` line in its charter. That brings the charter, its `SOUL.md`, and its `CARD.md` together, which is what the installer does for every star at once, plus the guide with its references.

The plugin and the skills CLI bring the stars and their working skills. The vault, the runner, the hooks, and the evals come only from `node ~/Downloads/stellar-agents/scripts/install.js --vault <dir>` in the unzipped release. See [docs/runtime.md](../../docs/runtime.md).

Back to the [main README](../../README.md).
