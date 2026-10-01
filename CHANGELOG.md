# Changelog

## 0.1.3

The README no longer suggests installing for every tool at once: the installer writes files only for the tools you name after `--tools`, for example `--tools codex`. No charter or skill changed.

## 0.1.2

The folder inside the zip is now always `stellar-agents`, with no version in its name, so the paths in this README stay right from release to release. The installer and the runner both work by full path from any Terminal window: `node ~/Downloads/stellar-agents/scripts/install.js --tools codex --vault ~/stellar`, then `python3 ~/stellar/scripts/newsroom.py run ...`. No charter or skill changed.

## 0.1.1

The install instructions pointed at `./stellar-agents`, a folder the download never makes: the zip unzips to `stellar-agents-v<version>`. Every install command now runs from inside the unzipped folder, starting with `cd` into it, and the native commands use `.` for the folder. The README leads with the kit's own installer, `node scripts/install.js --tools <tool> --vault ~/stellar`, because the native commands bring the skills only, with no vault and no runner. Mira's charter also catches up with Ascension's: only a box you ticked counts as done, and a staged draft is not done, because it still waits on you to send it. The free 0.1.0 had shipped the charter from before that fix.

## 0.1.0

The first release of Stellar Agents, the free kit.

Eight stars and their charters, cards, and voices: Draco the Chief of Staff, Carina the Managing Editor, Alcyone the Scheduler, Aurora the Reporter, Electra the Correspondent, Vesper the Copy Desk, Mira the Ombudsman, and Selene the Archivist. One of them works: Draco's morning brief writes one page into your Obsidian daily note from a calendar export and `todo.md`, counts what rolls over from day to day, and asks for a ruling at three.

The starter vault opens in Obsidian with daily notes pointed at `Daily/`, a brief template, and `Home.md`. The installer writes the stars into Claude Code, Codex, Gemini CLI, OpenClaw, and Hermes, and keeps a manifest so installing Stellar Agents Ascension over the same folder keeps everything you edited.
