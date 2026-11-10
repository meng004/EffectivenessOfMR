#!/usr/bin/env bash
# 3 files x 2 verdicts = 6 cosmic-ray sessions. Run from ~/mrtrial/harness with venv active.
# shortcut: command names per cosmic-ray 8.x; check `cosmic-ray --help` first (doc 3.7).
set -euo pipefail
H="$(cd "$(dirname "$0")" && pwd)"; RES="$H/../results"; D="$HOME/mrtrial/openmc/openmc/deplete"
for f in cram chain nuclide; do
  for v in mr oracle; do
    cfg="$RES/${f}_${v}.toml"
    cat > "$cfg" <<EOF
[cosmic-ray]
module-path = "$D/$f.py"
timeout = 60.0
excluded-modules = []
test-command = "cd $H && python run_$v.py"
[cosmic-ray.distributor]
name = "local"
EOF
    cosmic-ray init "$cfg" "$RES/${f}_${v}.sqlite"
    cosmic-ray exec "$cfg" "$RES/${f}_${v}.sqlite"
    git -C "$HOME/mrtrial/openmc" diff --quiet || { echo "source left mutated after $f/$v"; exit 1; }
  done
done
