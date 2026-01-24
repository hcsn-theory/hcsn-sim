import json
from engine.hypergraph import Hypergraph
from engine.rewrite_engine import RewriteEngine
from engine.observables import (
    worldline_interaction_graph,
    hierarchical_closure
)

# -------------------------------
# Parameters (match interaction)
# -------------------------------
STABILIZE_STEPS = 1200
OBSERVE_STEPS   = 8000
OMEGA_TARGET = 1.10
OMEGA_TOL = 0.05
SEED = 1

# -------------------------------
# Initialize universe
# -------------------------------
H = Hypergraph()
v1 = H.add_vertex()
v2 = H.add_vertex()
H.add_causal_relation(v1, v2)
H.add_hyperedge([v1, v2])

engine = RewriteEngine(H, seed=SEED)

# -------------------------------
# Reach target Ω
# -------------------------------
while True:
    engine.step()
    inter = worldline_interaction_graph(H)
    Omega = hierarchical_closure(H, inter)
    if abs(Omega - OMEGA_TARGET) < OMEGA_TOL:
        break

# -------------------------------
# Inject SINGLE proto-particle
# -------------------------------
success = engine.force_defect(magnitude=0.3)
if not success:
    raise RuntimeError("Proto-particle injection failed")

first_injection_time = engine.time

# -------------------------------
# Stabilize
# -------------------------------
for _ in range(STABILIZE_STEPS):
    engine.step()

# -------------------------------
# Observe (NO SECOND PARTICLE)
# -------------------------------
for _ in range(OBSERVE_STEPS):
    engine.step()

# -------------------------------
# Save control data
# -------------------------------
out = {
    "first_injection_time": first_injection_time,
    "rewrite_history": engine.rewrite_history,
}

with open("analysis/single_particle_control.json", "w") as f:
    json.dump(out, f, indent=2)

print("Saved → analysis/single_particle_control.json")