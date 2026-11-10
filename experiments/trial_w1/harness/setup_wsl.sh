#!/usr/bin/env bash
# WSL2 Ubuntu 24.04: build OpenMC v0.15.2 from source, editable Python install for mutation.
set -euo pipefail
ROOT="$HOME/mrtrial"; SRC="$ROOT/openmc"; RES="$ROOT/results"
mkdir -p "$RES"
sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  build-essential cmake git libhdf5-dev libpng-dev python3-venv python3-dev sqlite3
[ -d "$SRC" ] || git clone --depth 1 --branch v0.15.2 --recurse-submodules --shallow-submodules \
  https://github.com/openmc-dev/openmc.git "$SRC"
cmake -S "$SRC" -B "$SRC/build" -DCMAKE_BUILD_TYPE=Release -DHDF5_PREFER_PARALLEL=OFF \
  -DCMAKE_INSTALL_PREFIX="$ROOT/local"
cmake --build "$SRC/build" -j"$(nproc)"
cmake --install "$SRC/build"
python3 -m venv "$ROOT/venv"
source "$ROOT/venv/bin/activate"
pip install -q --upgrade pip
# editable: cosmic-ray edits these source files, so import must resolve here
pip install -q -e "$SRC" scipy cosmic-ray coverage
P=$(python -c "import openmc.deplete.cram as m; print(m.__file__)")
echo "cram.py -> $P"
case "$P" in "$SRC"/*) echo "OK editable";; *) echo "FAIL: not editable"; exit 1;; esac
{ uname -a; python --version; git -C "$SRC" rev-parse HEAD; cosmic-ray --version 2>&1 || true
  lscpu | grep -E 'Model name|^CPU\(s\)'; pip freeze; } > "$RES/env.txt"
echo "setup done; add to shell: export PATH=$ROOT/local/bin:\$PATH"
