#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$ROOT/data/uploads/posture"
mkdir -p "$ROOT/data/logs"
echo "OK: storage dirs prepared at $ROOT/data"
