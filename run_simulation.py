import time
import json
import sys
from datetime import datetime

from engine.hypergraph import Hypergraph
from engine.rewrite_engine import RewriteEngine
from engine.observables import (
    worldline_interaction_graph,
    interaction_concentration,
    closure_density,
    hierarchical_closure,
)

# ============================================================
# Configuration (EXPERIMENT-LEVEL ONLY)
# ============================================================

CONFIG = {
    "seed": 1,
    "max_steps": 1500,
    "sample_interval": 100,
    "log_file": "simulation.log",
    "timeseries_file": "timeseries.json",
}

# ============================================================
# Dual-output logger (terminal + file, append-only)
# ============================================================

class DualOutput:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.terminal.flush()
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()


sys.stdout = DualOutput(CONFIG["log_file"])

# ============================================================
# Initialize universe (NO PHYSICS TUNING HERE)
# ============================================================

H = Hypergraph()
v1 = H.add_vertex()
v2 = H.add_vertex()
H.add_causal_relation(v1, v2)
H.add_hyperedge([v1, v2])

engine = RewriteEngine(H, seed=CONFIG["seed"])

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

start_time = time.time()

# ============================================================
# Run header
# ============================================================

run_timestamp = datetime.now().isoformat()

print("\n" + "=" * 86)
print(f"RUN STARTED: {run_timestamp}")
print("=" * 86)

print(
    " time |   V   |  <k>  | Δ<k> |  L  | ΔL |"
    "    Φ    |    Ψ    | acc%   |   omega   |   domega"
)

# ============================================================
# Main evolution loop
# ============================================================

for _ in range(1, CONFIG["max_steps"] + 1):
    success = engine.step()
    if success:
        accepted += 1
    else:
        rejected += 1

    if engine.time % CONFIG["sample_interval"] != 0:
        continue

    inter = worldline_interaction_graph(H)

    k = H.average_coordination()
    L = H.max_chain_length()

    dk = k - last_k
    dL = L - last_L

    omega = hierarchical_closure(H, inter)
    domega = omega - last_omega

    # --- store time series ---
    timeseries_t.append(engine.time)
    timeseries_k.append(k)
    timeseries_omega.append(omega)

    acc_ratio = accepted / max(accepted + rejected, 1)

    print(
        f"{engine.time:5d} | "
        f"{len(H.vertices):5d} | "
        f"{k:5.2f} | "
        f"{dk:+5.2f} | "
        f"{L:3d} | "
        f"{dL:+3d} | "
        f"{interaction_concentration(inter):7.4f} | "
        f"{closure_density(inter):7.4f} | "
        f"{acc_ratio:5.2%}   | "
        f"{omega:7.4f} | "
        f"{domega:+7.4f} |"
    )

    last_k = k
    last_L = L
    last_omega = omega

# ============================================================
# Run summary
# ============================================================

end_time = time.time()

print("\nRun complete.")
print(f"Total steps: {engine.time}")
print(f"Accepted: {accepted}, Rejected: {rejected}")
print(f"Acceptance ratio: {accepted / max(accepted + rejected, 1):.3f}")
print(f"Wall time: {end_time - start_time:.2f} s")

# ============================================================
# Defect statistics
# ============================================================

print("\n================ DEFECT STATISTICS ================\n")

defects = engine.defect_log
print(f"Total defects detected: {len(defects)}")

if len(defects) > 1:
    times = [d["time"] for d in defects]
    spacings = [times[i + 1] - times[i] for i in range(len(times) - 1)]

    print(f"Average defect spacing: {sum(spacings) / len(spacings):.2f} steps")
    print(f"Min spacing: {min(spacings)}")
    print(f"Max spacing: {max(spacings)}")
    print("First 10 spacings:", spacings[:10])

# ============================================================
# Append time series to JSON (RUN-PRESERVING)
# ============================================================

run_record = {
    "run_started": run_timestamp,
    "config": CONFIG,
    "t": timeseries_t,
    "k": timeseries_k,
    "omega": timeseries_omega,
    "defects": defects,
}

try:
    with open(CONFIG["timeseries_file"], "r") as f:
        existing = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    existing = []

existing.append(run_record)

with open(CONFIG["timeseries_file"], "w") as f:
    json.dump(existing, f, indent=2)

print("Appended run to timeseries.json")
