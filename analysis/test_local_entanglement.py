import json
import numpy as np
from scipy.stats import pearsonr

def main():
    with open("analysis/local_omega_channels.json") as f:
        channels = json.load(f)

    print("\n=== Step 14.3: Local Ω Entanglement Test ===\n")

    if len(channels) < 2:
        print("Not enough channels.")
        return

    results = []

    for i in range(len(channels)):
        for j in range(i + 1, len(channels)):
            ci = channels[i]["channel"]
            cj = channels[j]["channel"]

            ti = np.array([x["time"] for x in ci])
            oi = np.array([x["omega_local"] for x in ci])

            tj = np.array([x["time"] for x in cj])
            oj = np.array([x["omega_local"] for x in cj])

            Δt = abs(ti.mean() - tj.mean())
            if Δt < 20:
                continue

            n = min(len(oi), len(oj))
            if n < 3:
                continue

            corr, _ = pearsonr(oi[:n], oj[:n])

            results.append((Δt, corr, (channels[i]["particle"], channels[j]["particle"])))

    if not results:
        print("No sufficiently separated pairs.")
        return

    for Δt, corr, pair in results:
        print(f"Pair {pair} | Δt={int(Δt)} | corr={corr:+.3f}")

    corrs = np.array([r[1] for r in results])

    print("\nSummary:")
    print(f"Mean correlation: {corrs.mean():+.3f}")
    print(f"Std: {corrs.std():.3f}")

    if abs(corrs.mean()) > 0.3:
        print("\n✅ STEP 14.3 PASSED")
    else:
        print("\n⚠ Weak correlation — refine topology tracking")

if __name__ == "__main__":
    main()