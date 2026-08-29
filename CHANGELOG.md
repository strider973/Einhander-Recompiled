# Changelog

All notable changes to Einhander Recompiled are documented here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## [0.1.3] - 2026-08-29

### Changed
- **Rebuilt from a clean project scaffold on the latest upstream framework** —
  `psxrecomp` `847d76f0` and `recomp-ui` `d8bbe1c` (both 2026-08-28). This
  pulls in the **SteamOS / immutable-filesystem self-compilation fixes**
  (`mstan/psxrecomp` `eefa4a9e` and related), so players on **SteamOS / Steam
  Deck** can Generate & build the title from their own legal disc without the
  earlier build errors. Windows and several Linux-distro self-build fixes are
  included as well, plus the framework hardening/hotfixes shipped upstream
  since the previous release.
- **`[video] vsync = "off"`** — on high-refresh displays (120 Hz+), driver
  vsync was pacing the emulator to the panel refresh rate, running the whole
  game at roughly 2x speed. The fixed 59.94 Hz wall-clock pacer now owns
  frame cadence.
- Carried runtime tuning: overlay compile cache + gcc overlay backend,
  widescreen offer off, lowered audio bridge buffer (30 ms), multitap analog.

### Notes
Same content policy as before: no game, no Sony BIOS, no save data or
copyrighted disc/cover assets. Status: experimental.

## [0.1.2] - 2026-08-26

### Changed
- Framework / launcher submodule bump; distribution hardening.

## [0.1.1] - 2026-08-22

### Fixed
- **FMV audio crackle / micro-cuts** — the host audio DRC ring buffer's
  overflow headroom was undersized for the low-latency profile (+40 ms
  floor), leaving only 45 ms of slack against the ~140 ms production
  pauses CD-XA sector delivery can cause during movie playback. The
  ring overflowed continuously during the intro FMV, dropping samples
  and producing audible crackle. Headroom is now sized off a +100 ms
  floor, matching the margin the shared audio bridge's own ecosystem
  defaults already validate.
- **Thin black vertical line on the right edge of 24-bit FMV frames**
  (visible on the title screen) — the present path unconditionally
  blanked the last 8 pixel columns of every depth24 frame as a safety
  margin against stale VRAM, a workaround written for a different
  title's genuinely-partial upload. It never checked whether the
  current frame's MDEC upload had already confirmed full-width
  coverage, so valid pixels were hidden on every frame regardless.

## [0.1.0] - 2026-08-21

First public Windows x64 test release.

### Added
- Recompiled Einhander runtime for SCUS-94243
- Unified launcher with keyboard and controller configuration
- OpenGL renderer and graphics options
- OpenBIOS included under its license
- Select your own legally dumped CUE file with Open *.cue

### Notes
Not included: the game, Sony BIOS, save data, or copyrighted disc/cover
assets. Status: experimental.
