import json
import numpy as np
from scipy.stats import pearsonr

def main():
    with open("analysis/particles.json") as f:
        particles = json.load(f)

    # Load omega history (from simulation log)
    with open("analysis/omega_timeseries.json") as f:
        omega_ts = json.load(f)

    omega_at_time = {o["time"]: o["omega"] for o in omega_ts}

    results = []

    print("\n=== Step 14.2: Topological Entanglement Test (Ω) ===\n")

    for pid, p in enumerate(particles):
        times = p["times"]
        if len(times) < 3:
            continue

        omegas = [omega_at_time[t] for t in times if t in omega_at_time]
        if len(omegas) < 3:
            continue

        dt = max(times) - min(times)

        # correlate early vs late Ω
        mid = len(omegas) // 2
        o1 = omegas[:mid]
        o2 = omegas[mid:]

        n = min(len(o1), len(o2))
        if n < 2:
            continue

        corr, _ = pearsonr(o1[:n], o2[:n])

        results.append((dt, corr))

        print(f"Particle {pid:2d} | Δt = {dt:4d} | Ω-corr = {corr:+.3f}")

    if len(results) < 3:
        print("\nNot enough data for global test.")
        return

    dts, corrs = zip(*results)
    r_global, _ = pearsonr(dts, corrs)

    print("\n--- Summary ---")
    print(f"Tested particles: {len(results)}")
    print(f"Ω-correlation vs causal separation r = {r_global:+.3f}")

    if abs(r_global) < 0.2:
        print("\n✅ TOPOLOGICAL ENTANGLEMENT OBSERVED")
        print("Ω correlations persist independent of causal distance.")
    else:
        print("\n⚠ Weak or decaying Ω correlation.")
        print("Topology tracking may require refinement.")

if __name__ == "__main__":
    main()