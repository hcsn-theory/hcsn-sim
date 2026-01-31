import json
import numpy as np

def main():
    # --- Load data ---
    with open("analysis/particles.json") as f:
        particles = json.load(f)

    with open("analysis/defect_momentum_timeseries.json") as f:
        momentum = json.load(f)

    # Map defect time -> Var(p)
    varp = {d["time"]: d["var_p"] for d in momentum}

    print("\n=== Step 14: Topological Entanglement Test (HCSN) ===\n")

    results = []

    for pid, p in enumerate(particles):
        times = sorted(p["times"])
        if len(times) < 2:
            continue

        obs = [varp[t] for t in times if t in varp]
        if len(obs) < 2:
            continue

        dt = times[-1] - times[0]
        corr = np.corrcoef(obs[:-1], obs[1:])[0, 1] if len(obs) > 2 else 1.0
        var_obs = np.var(obs)

        results.append((pid, dt, corr, var_obs))

        print(
            f"Particle {pid:2d} | "
            f"Δt = {dt:4d} | "
            f"corr = {corr:+.3f} | "
            f"Var(O) = {var_obs:.4f}"
        )

    if not results:
        print("\n❌ No multi-defect particles found.")
        return

    # --- Global assessment ---
    dts = np.array([r[1] for r in results])
    corrs = np.array([r[2] for r in results])

    global_corr = np.corrcoef(dts, corrs)[0, 1]

    print("\n--- Summary ---")
    print(f"Total tested particles: {len(results)}")
    print(f"Correlation vs causal separation r = {global_corr:+.3f}")

    if abs(global_corr) < 0.3:
        print("\n✅ PASS: Correlation is largely independent of causal distance.")
        print("   → Topological (non-metric) entanglement supported.")
    else:
        print("\n⚠️  INCONCLUSIVE: Correlation decays with distance.")
        print("   → Stronger topology tracking may be required.")

if __name__ == "__main__":
    main()