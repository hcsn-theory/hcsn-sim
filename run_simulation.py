import time
from engine.hypergraph import Hypergraph
from engine.rewrite_engine import RewriteEngine
from engine.observables import (
    worldline_interaction_graph,
    interaction_concentration,
    closure_density,
    hierarchical_closure
)

import sys

# --- Add this Logger Class ---
class DualOutput:
    def __init__(self, filename):
        self.terminal = sys.stdout
        # "a" mode appends to the file (keeping history)
        self.log = open(filename, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        # Flush immediately to update the file live
        self.log.flush()
        self.terminal.flush()

    def flush(self):
        # This flush method is needed for python 3 compatibility.
        self.terminal.flush()
        self.log.flush()

# Redirect python's print to our new class
sys.stdout = DualOutput("simulation.log")
# -----------------------------


# -----------------------------
# Initialize universe
# -----------------------------
H = Hypergraph()
v1 = H.add_vertex()
v2 = H.add_vertex()
H.add_causal_relation(v1, v2)
H.add_hyperedge([v1, v2])

engine = RewriteEngine(H, seed=1)

# -----------------------------
# Diagnostics state
# -----------------------------
accepted = 0
rejected = 0
last_k = H.average_coordination()
last_L = H.max_chain_length()
last_omega = hierarchical_closure(H, worldline_interaction_graph(H))

start_time = time.time()

# --- ADD THESE LINES ---
print("\n" + "="*86)
print(f"RUN STARTED: {time.ctime()}")  # Prints: Sat Oct 27 10:30:00 2023
print("="*86)
# -----------------------

print(
    " time |   V   |  <k>  | Δ<k> |  L  | ΔL |    Φ    |    Ψ    |    Ω    | acc%   |   omega   |   domega"
)
# ... rest of code ...

# -----------------------------
# Main evolution loop
# -----------------------------
for step in range(1, 5001):
    success = engine.step()
    if success:
        accepted += 1
    else:
        rejected += 1

    if engine.time % 100 == 0:
        inter = worldline_interaction_graph(H)

        k = H.average_coordination()
        L = H.max_chain_length()

        dk = k - last_k
        dL = L - last_L
        
        omega = hierarchical_closure(H, inter)
        domega = omega - last_omega

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
            f"{hierarchical_closure(H, inter):7.4f} | "
            f"{acc_ratio:5.2%}   | "
            f"{omega:7.4f} | "
            f"{domega:+7.4f} | "
        )

        last_k = k
        last_L = L
        last_omega = omega

end_time = time.time()

print("\nRun complete.")
print(f"Total steps: {engine.time}")
print(f"Accepted: {accepted}, Rejected: {rejected}")
print(f"Acceptance ratio: {accepted / max(accepted + rejected,1):.3f}")
print(f"Wall time: {end_time - start_time:.2f} s")
print("\n================ DEFECT STATISTICS ================\n")

defects = engine.defect_log

print(f"Total defects detected: {len(defects)}")

if len(defects) > 1:
    times = [d["time"] for d in defects]
    spacings = [times[i+1] - times[i] for i in range(len(times)-1)]

    avg_spacing = sum(spacings) / len(spacings)
    min_spacing = min(spacings)
    max_spacing = max(spacings)

    print(f"Average defect spacing: {avg_spacing:.2f} steps")
    print(f"Min spacing: {min_spacing}")
    print(f"Max spacing: {max_spacing}")

    print("\nFirst 10 spacings:")
    print(spacings[:10])
