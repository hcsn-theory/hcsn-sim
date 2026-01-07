import json
import sys
import numpy as np

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

front_times = []

for r in rewrites:
    t = r["time"]
    if t <= t0:
        continue

    xi_support = r.get("xi_support", [])
    if xi_support:
        front_times.append(t - t0)

if not front_times:
    print("\nNo ξ front detected.")
    sys.exit(0)

front_times = np.array(front_times)

print("\n=== ξ Propagation Speed ===")
print(f"Events detected : {len(front_times)}")
print(f"Min Δt          : {front_times.min()}")
print(f"Mean Δt         : {front_times.mean():.2f}")
print(f"Std Δt          : {front_times.std():.2f}")

# crude inverse speed proxy
v_eff = 1.0 / front_times.mean()
print(f"Effective propagation speed ~ {v_eff:.4f} (arb. units)")