# Changelog

All notable changes to Einhander Recompiled are documented here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

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
