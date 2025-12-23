#!/usr/bin/env python3
"""
run_simulation.py

Emergent spacetime simulation driver.
- Runs rewrite dynamics
- Logs diagnostics to console + file
- Detects and records topological defect events
- Stores append-only time series for plotting
"""

import time
import json
import sys
import os
from datetime import datetime

from engine.hypergraph import Hypergraph
from engine.rewrite_engine import RewriteEngine
from engine.observables import (
    worldline_interaction_graph,
    interaction_concentration,
    closure_density,
    hierarchical_closure
)

# ============================================================
# Dual output logger (console + file)
# ============================================================

class DualOutput:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()
        self.terminal.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

sys.stdout = DualOutput("simulation.log")

# ============================================================
# Initialize universe
# ============================================================

H = Hypergraph()

v1 = H.add_vertex()
v2 = H.add_vertex()
H.add_causal_relation(v1, v2)
H.add_hyperedge([v1, v2])

engine = RewriteEngine(
    H,
    seed=1,
    p_create=0.6,
    gamma_time=0.1,
    gamma_space=0.1,
    gamma_ext=0.05,
    gamma_closure=0.05,
    gamma_hier=0.06,
    epsilon_label_violation=1e-4
)

# ============================================================
# Diagnostics state
# ============================================================

accepted = 0
rejected = 0

last_k = H.average_coordination()
last_L = H.max_chain_length()
last_omega = hierarchical_closure(H, worldline_interaction_graph(H))

# ============================================================
# Time-series storage (for plotting)
# ============================================================

timeseries_t = []
timeseries_k = []
timeseries_omega = []

# ============================================================
# Run header
# ============================================================

run_start_wall = time.time()
run_id = datetime.now().isoformat(timespec="seconds")

print("\n" + "=" * 92)
print(f"RUN STARTED: {run_id}")
print("=" * 92)

print(
    " time |   V   |  <k>  | Δ<k> |  L  | ΔL |"
    "    Φ    |    Ψ    |    Ω    | acc%   |  omega  |  Δomega"
)

# ============================================================
# Main evolution loop
# ============================================================

TOTAL_STEPS = 3000
SAMPLE_INTERVAL = 100

for _ in range(TOTAL_STEPS):
    success = engine.step()

    if success:
        accepted += 1
    else:
        rejected += 1

    if engine.time % SAMPLE_INTERVAL == 0:
        inter = worldline_interaction_graph(H)

        k = H.average_coordination()
        L = H.max_chain_length()
        omega = hierarchical_closure(H, inter)

        dk = k - last_k
        dL = L - last_L
        domega = omega - last_omega

        acc_ratio = accepted / max(accepted + rejected, 1)

        # Store time series
        timeseries_t.append(engine.time)
        timeseries_k.append(k)
        timeseries_omega.append(omega)

        print(
            f"{engine.time:5d} | "
            f"{len(H.vertices):5d} | "
            f"{k:5.2f} | "
            f"{dk:+5.2f} | "
            f"{L:3d} | "
            f"{dL:+3d} | "
            f"{interaction_concentration(inter):7.4f} | "
            f"{closure_density(inter):7.4f} | "
            f"{omega:7.4f} | "
            f"{acc_ratio:6.2%} | "
            f"{omega:7.4f} | "
            f"{domega:+7.4f}"
        )

        last_k = k
        last_L = L
        last_omega = omega

# ============================================================
# Run summary
# ============================================================

run_end_wall = time.time()

print("\nRun complete.")
print(f"Total steps: {engine.time}")
print(f"Accepted: {accepted}, Rejected: {rejected}")
print(f"Acceptance ratio: {accepted / max(accepted + rejected, 1):.3f}")
print(f"Wall time: {run_end_wall - run_start_wall:.2f} s")

# ============================================================
# Defect statistics
# ============================================================

defects = engine.defect_log

print("\n================ DEFECT STATISTICS ================\n")
print(f"Total defects detected: {len(defects)}")

if len(defects) > 1:
    times = [d["time"] for d in defects]
    spacings = [times[i + 1] - times[i] for i in range(len(times) - 1)]

    print(f"Average defect spacing: {sum(spacings)/len(spacings):.2f}")
    print(f"Min spacing: {min(spacings)}")
    print(f"Max spacing: {max(spacings)}")

# ============================================================
# Append run to timeseries.json (append-only)
# ============================================================

run_record = {
    "run_id": run_id,
    "meta": {
        "steps": engine.time,
        "sample_interval": SAMPLE_INTERVAL,
        "seed": 1,
        "accepted": accepted,
        "rejected": rejected,
        "acceptance_ratio": accepted / max(accepted + rejected, 1),
        "wall_time_sec": round(run_end_wall - run_start_wall, 3),
    },
    "timeseries": {
        "t": timeseries_t,
        "k": timeseries_k,
        "omega": timeseries_omega
    },
    "defects": defects
}

if os.path.exists("timeseries.json"):
    with open("timeseries.json", "r") as f:
        data = json.load(f)
else:
    data = {"runs": []}

data["runs"].append(run_record)

with open("timeseries.json", "w") as f:
    json.dump(data, f, indent=2)

print(f"\nSaved run {run_id} to timeseries.json")
print("=" * 92)
