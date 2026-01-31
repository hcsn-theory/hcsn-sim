import json
import sys
import numpy as np

if len(sys.argv) < 2:
    print("Usage: python -m analysis.measure_xi_lifetime <forced_probe_*.json>")
    sys.exit(1)
    
path = sys.argv[1]
with open(path) as f:
    data = json.load(f)

rewrites = data["rewrite_history"]
defects = data["defects"]

forced = [d for d in defects if d.get("forced", False)]
if not forced:
    print("No forced defect found.")
    sys.exit(0)

t0 = forced[0]["time"]

times = []
# After loading rewrites and finding t0 (forced time)

xi_support_sizes = []

for r in rewrites:
    if r["time"] <= t0:
        continue

    xi_support = r.get("xi_support", [])
    xi_support_sizes.append(len(xi_support))

if not xi_support_sizes:
    print("No ξ support data.")
    sys.exit(0)

sizes = np.array(xi_support_sizes)

print("\n=== ξ Support Lifetime Measurement ===")
print(f"Samples              : {len(sizes)}")
print(f"Initial support size : {sizes[0]}")
print(f"Max support size     : {sizes.max()}")
print(f"Mean support size    : {sizes.mean():.2f}")

# crude growth estimate
dt = np.arange(len(sizes))
coef = np.polyfit(dt, sizes, 1)
print(f"Support growth rate (d|ξ|/dt) ≈ {coef[0]:.4f}")

mean = sizes.mean()
smax = sizes.max()

if mean < 0.1:
    print("❌ Subcritical (ξ does not propagate)")
elif mean < 0.75 and smax <= 1:
    print("⚠ Critical (ξ propagates but remains localized)")
else:
    print("✅ Supercritical (ξ transport phase)")