<p align="center">
  <img src="docs/media/banner.png" alt="universal-modder" width="100%">
</p>

<p align="center">
  <b>Skills, tools and a shared knowledge base that let any AI coding agent mod almost any PC game you own.</b><br>
  This fork is configured for Codex and its native chat image generation.<br>
  The agent finds the game, works out the engine and the route, reads the real code, builds the mod, prepares 2D art,
  tests it in the running game, and writes down what it learned for the next agent.
</p>

<p align="center">
  <a href="#install"><img alt="Codex" src="https://img.shields.io/badge/agent-Codex-B6FF3B?labelColor=0A0D12"></a>
  <a href="knowledge/INDEX.md"><img alt="knowledge base" src="https://img.shields.io/badge/knowledge%20base-field%20notes-B6FF3B?labelColor=0A0D12"></a>
  <a href="skills/codex-assets/SKILL.md"><img alt="2D art in Codex" src="https://img.shields.io/badge/2D%20assets-Codex-B6FF3B?labelColor=0A0D12"></a>
  <a href="LICENSE"><img alt="MIT" src="https://img.shields.io/badge/license-MIT-B6FF3B?labelColor=0A0D12"></a>
</p>

<p align="center">
  <img src="docs/media/teaser.gif" alt="A tactical nuke in Terraria and robotaxis in Age of Empires II, both built with universal-modder" width="560">
</p>

## Install

Install the plugin into Codex, then start a new chat so its skills are discovered:

```powershell
codex plugin marketplace add thisisfortiktok259-ux/universal-modder
codex plugin add universal-modder@universal-modder-codex
```

Install the local CLI separately. The skills use the Agent Skills format, and the CLI handles local asset preparation and modding tools.

```powershell
git clone https://github.com/thisisfortiktok259-ux/universal-modder
cd universal-modder
python -m pip install .
python -m um --help
```

The plugin loads `skills/` directly. A checkout also includes `AGENTS.md` and links under `.agents/skills`; on Windows, Git may check out those links as plain text, so prefer the plugin install for skill discovery. On Windows, `python -m um` or `bin\um.cmd` works even when the `um` executable is not on PATH. Python 3.10+ is required.

**2D assets:** ask Codex in this chat to generate or edit a sprite with a transparent background, save the PNG, then use `um sprite` for the game's exact size and format. `um assets request` can write a reusable brief and `um assets import` can copy the generated PNG while recording a manifest. These CLI commands do not call an image model. The native chat tool cannot be invoked by a standalone CLI, and this workflow needs no fal or OpenAI API key. For 3D, audio and video, use licensed source files or local tools. ffmpeg is needed for video; Blender is needed for 3D → sprite renders.
Windows games are driven natively or from WSL.

## Try it
> Mod Terraria: add a homing missile launcher and a tactical nuke that craters the world. Make the sprites with Codex's native image generation.

> Make a new civilization for Age of Empires II with a unique unit rendered from 3D.

> Put real Minecraft inside GTA V story mode. Minecraft's camera should follow GTA's, and its TNT should blow up GTA cars.

> What engine is `C:\Games\Foo`, and has anyone modded it before?

The agent starts with the **mod-any-game** skill and runs the same loop every time:
1. search the knowledge base;
2. recon, then pick a route;
3. set up a safe lab (saves backed up);
4. read the actual code;
5. build one working slice;
6. generate assets;
7. verify in the real game;
8. record;
9. package;
10. write a field note for the next agent.

## A knowledge base that AIs write for AIs
[`knowledge/`](knowledge/) holds **field notes**: how specific games were actually modded, decompiled and
reverse-engineered. Each note gives:
- the exact versions that worked;
- the route, and why;
- what the engine really does;
- how it was verified;
- the gotchas (symptom → cause → fix).

**Every agent that finishes a mod can open a pull request with its note**, so the next agent starts where it
left off instead of rediscovering the same traps.

```bash
um kb search "grand theft auto"                 # before you start: prior art (works outside the repo too)
um kb new --game "Hades II" --title "A new boon god" --from-scan hades --agent "Codex (gpt-6)"
um kb check knowledge/games/hades-ii/a-new-boon-god.md
um kb pr knowledge/games/hades-ii/a-new-boon-god.md --yes    # after your human says OK: branch, push, PR
```
Browse [`knowledge/INDEX.md`](knowledge/INDEX.md). Contribution rules, for humans and AIs, are in
[`CONTRIBUTING.md`](CONTRIBUTING.md): no game files, no decompiled dumps, nothing that helps cheat online,
and an honest status and verification.

## What's inside

**Skills** (`skills/`, Agent Skills format)

| Skill | What it does |
|---|---|
| `mod-any-game` | The whole loop, hard safety rules, and **12 engine playbooks**: Unity, Unreal, .NET/XNA (Terraria, Stardew, Celeste), Godot, Source 1/2, Bethesda, Minecraft, AoE2/Genie, RE Engine/FromSoft/GTA/Cyberpunk/BG3, native C++, indie engines (GameMaker, RPG Maker, Ren'Py, Paradox, Doom, HTML5, LÖVE, Java), retro decomps |
| `game-recon` | Prior field notes, engine and version, managed or native, anti-cheat, loaders, save folders, community route → `MODDING_PLAN.md` |
| `reverse-engineering` | ILSpy / Cpp2IL / Vineflower / Ghidra and IDA over MCP / Cheat Engine / Frida / RenderDoc; reverse-engineer a file format and prove it with a round trip |
| `codex-assets` | Create or edit 2D sprites, icons, concepts and textures in the Codex chat; save PNGs and record local provenance |
| `asset-pipeline` | Art → engine-exact frames: cutout, nearest-neighbour fit, palettes, sheets, team-colour masks, 3D → 8/16-heading sprites |
| `game-automation` | Launch, screenshot (GPU-safe), click/type safely, windowed mode, crash-reporter cleanup, in-game agent bridges |
| `showcase-video` | Record the window with only the game's audio, pick moments, cut a styled video from an EDL |
| `mashup-mods` | Game inside a game: content ports, passthrough mods (worked example: Minecraft × GTA V), decomps as libraries, reimplementations |
| `publish-mod` | Lint, package per platform, credits, the post |
| `share-field-notes` | Search the knowledge base, write your own note, open the PR |

**The `um` CLI** (Python). Every command has `--help` with examples.

| | |
|---|---|
| `um scan` | Find Steam/Epic/Xbox installs; fingerprint engine and version, .NET vs native, anti-cheat, installed loaders, save folders, ranked routes |
| `um assets` | `request` writes a local 2D generation brief; `import` copies a completed PNG and records its provenance |
| `um sprite` | `cutout`, `fit`, `pixelate`, `palette`, `sheet`, `slice`, `frames`, `team-mask`, `seamless`, `preview` |
| `um render3d` | GLB → sprite frames from the game's camera (`aoe2`, `iso8`, `trueiso`, `topdown`, `side`, `turntable`) with Blender |
| `um win` | `shot`, `record` (gfxcapture + process-loopback audio), `drive` (input that only reaches the game), `ps`, `kill`, `launch`, `reg` |
| `um video` | `contact` sheets, `compile` (EDL → titled, beat-cut video with music), `mux`, `beats`, `first-frame` |
| `um backup` | Snapshot, diff and restore save folders |
| `um publish check` | Blocks shipping game files, decompiled code and leaked keys |
| `um kb` | The knowledge base: `search`, `show`, `new`, `check`, `index`, `sync`, `pr` |

Two no-build Windows tools ship inside the package (`um/ps1/`): WinDrive input and ProcLoopback game-only
audio, both PowerShell with embedded C#.

The local 2D pipeline is: Codex chat image → PNG → `um assets import` (optional) → `um sprite` → in-game check. The archived examples below used fal and retain their original credits.

## Built with it
- **[examples/terraria-tmodloader](examples/terraria-tmodloader)**: *Fal Arsenal* for tModLoader.
  - Weapons: a homing missile launcher, a tactical nuke (crater + mushroom cloud), a chain-lightning rifle, a
    black-hole gun and an orbital strike.
  - Three new enemies and a two-phase Drone Mothership boss.
  - Every sprite came from fal.
- **[examples/aoe2-de-civ](examples/aoe2-de-civ)**: *San Franciscans* for Age of Empires II DE.
  - A new civilization with a Robotaxi unique unit and Delivery Drones, rendered from fal image-to-3D models
    at AoE2's camera angle.
  - A Transamerica Pyramid wonder.
  - A reverse-engineered `.sld` sprite writer.
- **[examples/minecraft-gta5-passthrough](examples/minecraft-gta5-passthrough)**: real Minecraft inside
  GTA V story mode.
  - A Fabric mod and a ScriptHookV + ReShade add-on exchange camera, ground and events over a local
    WebSocket.
  - Minecraft's colour + depth are depth-composited into GTA's frame.
  - Minecraft TNT, arrows and fireworks become GTA explosions and bullets, and Minecraft mobs fight the
    police.

Each has a field note with every non-obvious lesson: [knowledge/INDEX.md](knowledge/INDEX.md).

## Rules it follows
- **Single-player and offline, on games you own.** It refuses to inject into online games with anti-cheat,
  write multiplayer cheats, or bypass anti-cheat, DRM or ownership checks.
- **It never ships game files or decompiled code.** Mods ship as code, your own assets, patches or
  converters.
- **It backs up before touching saves**, and kills processes by PID only.
- **It asks before** driving your mouse and keyboard, installing loaders into game folders, or publishing,
  PRs included.

Full reasoning: [`skills/mod-any-game/references/safety.md`](skills/mod-any-game/references/safety.md).

## Credits
- Built from real agent sessions modding Terraria, Age of Empires II and GTA V × Minecraft.
- The archived example assets were generated with [fal](https://fal.ai); their provenance has not been relabeled. New 2D assets in this fork use the available Codex chat image tool.
- Standing on the shoulders of tModLoader, genieutils-py, AoE2ScenarioParser, ScriptHookV, ReShade, Fabric,
  BepInEx, Harmony, UE4SS, REFramework, SKSE, ILSpy, Ghidra and every modding community that documented its
  game.
- The engine playbooks also draw on the September 2026 wave of AI-built mods, and on how their creators
  explained them in public.

MIT licensed. Fonts: Space Grotesk and JetBrains Mono (SIL OFL).
