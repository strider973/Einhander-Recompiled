# Einhänder Recompiled

<p align="center">
  <img src="assets/psxrecomp.png" width="128" alt="Einhänder Recompiled icon">
</p>

Experimental PC recompilation project for the US PlayStation release of
**Einhänder** (`SCUS-94243`), powered by
[PSXRecomp](https://github.com/mstan/psxrecomp).

> [!IMPORTANT]
> This is an early work in progress, not an official Square Enix release.
> You must provide your own legally obtained game dump. No game image, BIOS,
> copyrighted game data, or decryption material is included.

## Current status

| Feature | Status |
|---|---|
| Boot and gameplay | Working |
| Tested progression | Through Stage 3 |
| Framerate | 60 FPS |
| Audio and music | Working; occasional minor audio artifacts may remain |
| Keyboard | Working, configurable in the launcher |
| Controllers | Working, configurable in the launcher |
| Memory cards | Working |
| Save states and rewind | Experimental |
| Display | Original 4:3 presentation |
| Renderer | OpenGL recommended |

Compatibility beyond the tested stages is not yet guaranteed. Please report a
problem with the stage, route, renderer, settings used, and a screenshot when
possible.

## Features

- Native Windows executable produced from recompiled PS1 code
- Integrated launcher
- Keyboard and controller remapping
- Configurable internal resolution, antialiasing, texture filtering and VSync
- Memory-card support
- Save states and rewind tools for testing
- Optional OpenBIOS/HLE startup path

## Requirements

- 64-bit Windows
- A GPU with modern OpenGL support
- Your own US Einhänder disc dump (`BIN` + `CUE`)
- The original game serial must be `SCUS-94243`

## Running the game

1. Place your legally dumped `BIN` and `CUE` files somewhere on your computer.
2. Start `Einhander_Recompiled.exe`.
3. Use **Change Disc** in the launcher and select the `CUE` file.
4. Configure the keyboard or controller if needed, then select **Play**.

The launcher remembers the selected disc path locally. Disc images, memory
cards and personal settings are intentionally excluded from this repository.

## Recommended graphics settings

- Renderer: **OpenGL**
- Aspect ratio: **4:3**
- Texture filtering: **Nearest** for the original PS1 look
- Supersampling: **2x** or higher if performance allows
- VSync: **On**

Einhänder was authored for 4:3. Widescreen is currently disabled because a
generic wider view exposes empty areas outside some original backgrounds.

## Building from source

```bash
git submodule update --init --recursive
powershell -ExecutionPolicy Bypass -File scripts/apply_framework_patches.ps1
python psxrecomp/psxrecomp_cli.py generate --config game.toml --project-root . --disc "path/to/Einhaender.cue"
cmake -S . -B build-release -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build-release --target psx-runtime
```

The exact toolchain setup is documented in
[`psxrecomp/docs/GAME_PROJECT_SETUP.md`](psxrecomp/docs/GAME_PROJECT_SETUP.md).

## Known limitations

- Only the US release identified by `SCUS-94243` is currently targeted.
- Some alternate routes and later stages still need extended testing.
- Save states are development-oriented and may become incompatible after an
  update.
- Minor audio artifacts may occasionally occur.

## Credits

- Original game: Square, 1997
- Original PlayStation hardware and branding: Sony Computer Entertainment
- Recompilation framework: [Matthew Stan — mstan/psxrecomp](https://github.com/mstan/psxrecomp)
- Launcher framework: [Matthew Stanley — mstan/recomp-ui](https://github.com/mstan/recomp-ui)

## Licensing and attribution

- `psxrecomp` is distributed under the
  [PolyForm Noncommercial License 1.0.0](psxrecomp/LICENSE).
- `recomp-ui` is distributed under the [MIT License](recomp-ui/LICENSE).
- Their copyright notices and license files remain included in their respective
  submodules.
- The launcher icon is derived from the PSXRecomp project assets and is subject
  to the applicable PSXRecomp license.
- No ownership is claimed over Einhänder, its characters, artwork, music,
  trademarks or other original game content.

This project is unaffiliated with and not endorsed by Square Enix or Sony
Interactive Entertainment. All trademarks belong to their respective owners.
