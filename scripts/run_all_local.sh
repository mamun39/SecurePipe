#!/usr/bin/env bash
set -euo pipefail
. .venv/bin/activate || true
make scan-all || true
echo "Done. See reports/ for outputs."