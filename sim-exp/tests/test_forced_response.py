import json
import sys
import numpy as np

path = sys.argv[1]
with open(path) as f:
    data = json.load(f)

defects = data["defects"]
rewrites = data["rewrite_history"]

forced = [d for d in defects if d.get("forced", False)]
if not forced:
    print("No forced defect found.")
    sys.exit(0)

forced = forced[0]
t0 = forced["time"]
anchor = forced.get("anchor_vertex")

print(f"\n=== Forced Response Analysis ===")
print(f"Forced defect at t = {t0}, Ω = {forced['omega']:.3f}")

if anchor is None:
    print("❌ Forced anchor missing.")
    sys.exit(0)


# ---------------------------------------
# ξ-propagation test (CORRECT)
# ---------------------------------------
WINDOW = 200
xi_rewrites = 0
total_rewrites = 0

for r in rewrites:
    t = r["time"]
    if t <= t0 or t > t0 + WINDOW:
        continue

    total_rewrites += 1
    if r.get("xi_support"):
        xi_rewrites += 1

ratio = xi_rewrites / total_rewrites if total_rewrites else 0.0

print("\n=== ξ Propagation Test ===")
print(f"Post-forcing rewrites      : {total_rewrites}")
print(f"Rewrites carrying ξ        : {xi_rewrites}")
print(f"ξ participation ratio     : {ratio:.3f}")

if ratio > 0.3:
    print("✅ ξ propagation detected")
elif ratio > 0.1:
    print("⚠ Weak ξ propagation")
else:
    print("❌ No ξ propagation")