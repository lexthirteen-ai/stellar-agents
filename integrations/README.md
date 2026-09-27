# Integrations

One page per tool: the command its users already know, where the files land, and how to call a star. Every command runs from the unzipped release folder. Every page also names the kit's own installer, which does all five at once: `node scripts/install.js --tools all`.

| Tool | Page |
|---|---|
| Claude Code | [claude-code](claude-code/README.md) |
| Codex | [codex](codex/README.md) |
| Gemini CLI | [gemini-cli](gemini-cli/README.md) |
| OpenClaw | [openclaw](openclaw/README.md) |
| Hermes | [hermes](hermes/README.md) |

Codex, Gemini CLI, and OpenClaw all read `~/.agents/skills/` as well as their own folder, so one install often serves all three. Claude Code and Hermes read their own folders, which is why the installer writes those too.

Any other tool that reads the Agent Skills format can pull the stars from the folder with `npx skills add ./stellar-agents`. The stars are plain skill folders, so nothing about them is tied to the five tools above.

Back to the [main README](../README.md).
