# analysis/measure_effective_potential.py

import json
import sys
import math
from collections import defaultdict

def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0

def main(path):
    with open(path) as f:
        data = json.load(f)

    rewrites = data.get("rewrite_history", [])
    if not rewrites:
        print("❌ No rewrite history available")
        return

    # --- accumulate rewrite flux per cluster ---
    cluster_flux = defaultdict(int)
    cluster_lifetime = defaultdict(int)

    for r in rewrites:
        cluster_ids = r.get("cluster_ids", [])
        if not cluster_ids:
            continue

        touched = r.get("xi_support", [])
        for cid in cluster_ids:
            cluster_flux[cid] += len(touched)
            cluster_lifetime[cid] += 1

    if len(cluster_flux) < 2:
        print("❌ Need ≥2 clusters for effective potential")
        return

    # sort clusters by total flux
    clusters = sorted(cluster_flux.keys())
    A, B = clusters[:2]

    Φ_A = cluster_flux[A] / max(cluster_lifetime[A], 1)
    Φ_B = cluster_flux[B] / max(cluster_lifetime[B], 1)

    # --- baseline: early-time average ---
    early_flux = []
    for r in rewrites[: max(50, len(rewrites)//10)]:
        touched = r.get("xi_support", [])
        early_flux.append(len(touched))

    Φ_baseline = mean(early_flux)

    ΔΦ = (Φ_A + Φ_B) - Φ_baseline
    V_eff = -ΔΦ

    print("\n=== Effective Potential from Rewrite Suppression (D1) ===\n")
    print(f"Cluster A ID     : {A}")
    print(f"Cluster B ID     : {B}")
    print(f"⟨Φ_A⟩           : {Φ_A:.6f}")
    print(f"⟨Φ_B⟩           : {Φ_B:.6f}")
    print(f"Φ_baseline      : {Φ_baseline:.6f}")
    print(f"ΔΦ              : {ΔΦ:.6f}")
    print(f"V_eff = -ΔΦ     : {V_eff:.6f}")

    if V_eff < 0:
        print("✅ Attractive effective potential detected")
    else:
        print("⚠ No attractive potential (repulsive or neutral)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 -m analysis.measure_effective_potential <interaction_experiment.json>")
        sys.exit(1)

    main(sys.argv[1])