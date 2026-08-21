#!/usr/bin/env bash
# Thin wrapper around the shared psxrecomp setup-host packager.
# Autofilled by tools/new_project_layout/setup_project.{sh,ps1}.
#
# Usage:
#   scripts/package_setup_release.sh <build-dir> <artifact-tag> [recompiler-build-dir]
#
# Writes: dist/ein-<VERSION>-<artifact-tag>.zip
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_DIR="${1:-}"
ARTIFACT_TAG="${2:-}"
RECOMPILER_BUILD="${3:-build-recompiler}"

if [[ -z "${BUILD_DIR}" || -z "${ARTIFACT_TAG}" ]]; then
  echo "usage: $0 <build-dir> <artifact-tag> [recompiler-build-dir]" >&2
  exit 2
fi

PACKAGER="${ROOT}/psxrecomp/tools/package_setup_host.sh"
if [[ ! -f "${PACKAGER}" ]]; then
  echo "error: missing ${PACKAGER} (psxrecomp submodule)" >&2
  exit 1
fi
chmod +x "${PACKAGER}" 2>/dev/null || true

EXTRA_PROJECT=()
if [[ -f "${ROOT}/catalog_identity.json" ]]; then
  EXTRA_PROJECT+=(--project-file catalog_identity.json)
fi
if [[ -f "${ROOT}/framework_pins.txt" ]]; then
  EXTRA_PROJECT+=(--project-file framework_pins.txt)
fi
# Optional in-game options defaults (titles that POST_BUILD-copy this file).
if [[ -f "${ROOT}/game_options.toml" ]]; then
  EXTRA_PROJECT+=(--project-file game_options.toml)
fi

cd "${ROOT}"
exec bash "${PACKAGER}" \
  --root "${ROOT}" \
  --build-dir "${BUILD_DIR}" \
  --artifact "${ARTIFACT_TAG}" \
  --zip-prefix ein \
  --exe-name Einhander_Recompiled \
  --display-name "Einhander Recompiled" \
  --recompiler-build "${RECOMPILER_BUILD}" \
  --version-env RELEASE_VERSION \
  --disc-hint "your legally owned Einhander disc" \
  --project-file CMakeLists.txt \
  --project-file game.toml \
  --project-file VERSION \
  --project-file codegen_setup.c \
  --project-file codegen_setup.h \
  --project-file README.md \
  --project-dir seeds \
  --project-dir launcher_assets \
  "${EXTRA_PROJECT[@]}"
