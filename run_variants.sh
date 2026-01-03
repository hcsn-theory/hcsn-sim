#!/usr/bin/env bash
set -e

VARIANTS=(
  "variant_1 0.15 1.0 1.02"
  "variant_2 0.20 1.0 1.02"
  "variant_3 0.15 2.0 1.02"
  "variant_4 0.15 1.0 1.05"
)

for V in "${VARIANTS[@]}"; do
  read NAME GAMMA INERTIA BOOST <<< "$V"

  echo "=== Running $NAME ==="

  export HCSN_GAMMA_DEFECT=$GAMMA
  export HCSN_INERTIA_SCALE=$INERTIA
  export HCSN_INTERACTION_BOOST=$BOOST

  python3 run_simulation.py

  python3 -m analysis.track_particles
  python3 -m analysis.measure_signal_speed
  python3 -m analysis.export_lorentz_cone
  python3 -m analysis.export_effective_eom
  python3 -m analysis.export_particle_stats

  mkdir -p $NAME
  cp analysis/particle_stats.json $NAME/
  cp analysis/effective_eom.json  $NAME/
  cp analysis/lorentz_cone.json   $NAME/
  cp analysis/signal_speeds.npy   $NAME/

  echo "Saved results to $NAME"
  echo
done
