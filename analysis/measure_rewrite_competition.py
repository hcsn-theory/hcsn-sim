# analysis/measure_rewrite_competition.py

import json
import sys
from collections import defaultdict

path = sys.argv[1]
with open(path) as f:
    data = json.load(f)

rewrites = data["rewrite_history"]
t2 = data["second_injection_time"]

touch_A = []
touch_B = []

for r in rewrites:
    if r["time"] < t2:
        continue

    cids = r.get("cluster_ids", [])
    if not cids:
        continue

    if 0 in cids:
        touch_A.append(r["time"])
    if 1 in cids:
        touch_B.append(r["time"])

print("\n=== Rewrite Competition Diagnostic ===")
print(f"Rewrites touching A: {len(touch_A)}")
print(f"Rewrites touching B: {len(touch_B)}")

if len(touch_A) != len(touch_B):
    print("✅ Competitive interaction via rewrite suppression")
else:
    print("❌ No competitive asymmetry")