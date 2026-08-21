# Preloaded mods

Ship reviewed, default-disabled packages here:

```text
packages/<package-id>/<version>/
  manifest.toml
  ...
```

Build wiring copies `mods/preloaded` next to the game executable as `mods/`.
Install player `.psxmod` archives through the launcher Mods manager instead of
committing them here. See `psxrecomp/docs/MOD_PACKAGES.md`.
