#!/usr/bin/env bash
set -euo pipefail

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
export PYTHONPATH="${repo_root}/builder${PYTHONPATH:+:${PYTHONPATH}}"
exec python3 -m unittest -v tests.test_kartpad_builder tests.test_rmcj01_profile tests.test_rmcj01_course_assets
