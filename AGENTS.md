# universal-modder

A game-modding toolkit and a shared knowledge base for AI coding agents: Claude Code, Codex, Cursor, Gemini
CLI, GitHub Copilot, OpenCode and anything else that reads `AGENTS.md`. When someone opens an agent in this
repo, they almost always want to **mod a game**, or to learn how a game was modded.

## Start here
1. **Read `skills/mod-any-game/SKILL.md` and follow its loop:** intake → recon → route → lab (backups) →
   source of truth → vertical slice → assets → verify in the real game → showcase → publish.
2. **Search the knowledge base first:** `bin/um kb search "<game or engine>"`. Other agents may already have
   written down the exact versions, routes and gotchas (`knowledge/INDEX.md`).
3. **At the end, share what you learned:** write a field note (`bin/um kb new ...`) and, once your human
   agrees, open a PR (`bin/um kb pr <note> --yes`). See `knowledge/README.md` and `CONTRIBUTING.md`.

## Tools
- **`bin/um`** is the Python CLI, and it sets itself up with `uv`.
  - Put it on PATH: `export PATH="$PWD/bin:$PATH"`, or install this fork with
    `python -m pip install .` and run `python -m um` (also works on Windows).
  - Every group has `--help`:
    - `scan`: installed games, engine, anti-cheat, loaders, saves, routes
    - `assets`: local 2D request briefs and imported PNG provenance; generation happens in Codex chat
    - `sprite` / `render3d`: art → engine-ready frames
    - `win`: launch, screenshot, input, record on Windows (also from WSL)
    - `video`: contact sheets and EDL showcase edits
    - `backup`: snapshot and restore saves
    - `publish`: pre-release lint
    - `kb`: the knowledge base
- **2D creation:** use Codex's native chat image tool when available, then save a PNG and process it
  with `um sprite`. `um assets request` and `um assets import` record a brief and provenance locally;
  neither invokes image generation. A standalone CLI cannot call the chat tool. Use licensed files or
  local tools for 3D, audio and video.
- **Skills** (`skills/*/SKILL.md`, Agent Skills format) are also linked where agents look for them:
  `.agents/skills` (Codex and others), `.claude/skills`, `.gemini/skills`, `.github/skills`.
- **Engine playbooks:** `skills/mod-any-game/references/engines/`.
- **Worked examples:** `examples/terraria-tmodloader`, `examples/aoe2-de-civ`,
  `examples/minecraft-gta5-passthrough`.

## Rules (full reasoning in `skills/mod-any-game/references/safety.md`)
- **What you can mod:** only games the user owns, single-player/offline.
  - Never touch online clients protected by anti-cheat.
  - Never write multiplayer cheats.
  - Never bypass anti-cheat, DRM or ownership checks.
- **Saves:** `um backup` saves before modded launches.
- **What you ship:** never commit or publish game files, extracted assets or decompiled code. Keep
  decompiles outside the repo.
- **Processes:** kill by exact PID (`um win kill`), never by name pattern.
- **Ask first** before:
  - driving the user's mouse and keyboard, and never focus a game with an online mode while they're typing;
  - installing loaders into game folders or changing the registry;
  - publishing anything, PRs included.
- **Keep a journal:** a `MODLOG.md` in the mod's working folder. It becomes your field note at the end.

## Working on the toolkit itself
- **Python:** 3.10+, deps Pillow, numpy and PyYAML (`uv` handles them via `bin/um`). Code lives in `um/`,
  one module per CLI group, each with `register(sub)` and a docstring that doubles as `--help`.
- **Windows tools:** `um/ps1/*.ps1` embed C# 5 (Windows PowerShell 5.1's compiler): no string
  interpolation, no `out var`, no expression-bodied members.
- **Tests:** `uv run --with pytest pytest -q tests`. CI also runs `um kb check --index` and
  `um publish check .`.
- **Wording:** keep skills and docs agent-neutral ("the agent", not a product name) except in sections
  about one specific agent.
