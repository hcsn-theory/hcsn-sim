import json
import glob
import numpy as np

files = sorted(glob.glob("analysis/forced_probe_*.json"))

results = []

for path in files:
    with open(path) as f:
        data = json.load(f)

    Omega = data.get("Omega_target", None)
    rewrites = data["rewrite_history"]
    defects = data["defects"]

    forced = [d for d in defects if d.get("forced", False)]
    if not forced:
        continue

    t0 = forced[0]["time"]

    post = [
        r for r in rewrites
        if r["time"] > t0
    ]

    total = len(post)
    xi_hits = sum(
        1 for r in post if r.get("xi_support")
    )

    ratio = xi_hits / total if total > 0 else 0.0
    results.append((Omega, ratio))

results = sorted(results)

print("\n=== Ω Phase Scan ===")
for Omega, ratio in results:
    print(f"Ω = {Omega:.3f} | ξ participation = {ratio:.3f}")