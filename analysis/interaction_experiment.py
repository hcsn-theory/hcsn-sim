# analysis/interaction_experiment.py

import json
import time
import math

from engine.hypergraph import Hypergraph
from engine.rewrite_engine import RewriteEngine
from engine.observables import (
    worldline_interaction_graph,
    hierarchical_closure,
)

# -------------------------------
# Experiment parameters
# -------------------------------
STABILIZE_STEPS = 600
INTERACTION_STEPS = 1500
OMEGA_TARGET = 1.10
OMEGA_TOL = 0.05
SEED = 1

# -------------------------------
# Geometry gating (CRITICAL)
# -------------------------------
MIN_XI_SUPPORT_FOR_GEOMETRY = 8
MIN_CLUSTER_COUNT = 2
GEOMETRY_START_DELAY = 50

# 🔧 ADDITION (observer throttle only)
GEOMETRY_STRIDE = 5        # compute geometry every N steps
MAX_BFS_DEPTH = 12         # cap physical distance search


# -------------------------------
# Initialize universe
# -------------------------------
H = Hypergraph()
v1 = H.add_vertex()
v2 = H.add_vertex()
H.add_causal_relation(v1, v2)
H.add_hyperedge([v1, v2])

engine = RewriteEngine(
    H,
    seed=SEED,
)

engine.topo_distance_memory = {}
engine.xi_distance_memory = {}

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
# Inject first proto-particle
# -------------------------------
if not engine.force_defect(magnitude=0.3):
    raise RuntimeError("First proto-particle injection failed")

first_injection_time = engine.time

for _ in range(STABILIZE_STEPS):
    engine.step()


# -------------------------------
# Safety reseed (ξ must exist)
# -------------------------------
if not engine.xi:
    seed_v = next(iter(engine.H.vertices.keys()))
    engine.xi[seed_v] = 0.2
    print(f"[inject] re-seeded ξ at v={seed_v}")


# -------------------------------
# Inject second proto-particle
# -------------------------------
if not engine.force_second_proto_object(
    omega_kick=0.3,
    xi_seed=1.0,
    min_distance=10,
):
    raise RuntimeError("Second proto-particle injection failed")

second_injection_time = engine.time


# -------------------------------
# Interaction observation
# -------------------------------
interaction_log = []

for _ in range(INTERACTION_STEPS):
    t0 = time.perf_counter()
    
    accepted = engine.step()
    if engine.time % 200 == 0:
        print(
            f"[geom-live] topo={len(engine.topo_distance_memory)} "
            f"xi={len(engine.xi_distance_memory)}"
        )
    
    t1 = time.perf_counter()

    # 🔧 ADDITION: reuse cached interaction graph if available
    if hasattr(engine, "_cached_inter"):
        inter = engine._cached_inter
    else:
        inter = worldline_interaction_graph(H)

    # --------------------------------
    # Geometry enable conditions
    # --------------------------------
    xi_mass = sum(
        1 for x in engine.xi.values()
        if x > engine.xi_threshold and math.isfinite(x)
    )

    # ξ support
    if engine.time % GEOMETRY_STRIDE == 0:
        
        xi_support = {
            int(v): float(x)
            for v, x in engine.xi.items()
            if x > engine.xi_threshold and math.isfinite(x)
        }
    else:
        xi_support = {}
    # --------------------------------
    # Read geometry from engine (OPTION B)
    # --------------------------------
    topo_geometry = {
        f"{a},{b}": float(d)
        for (a, b), d in engine.topo_distance_memory.items()
    }
    
    xi_geometry = {
        f"{a},{b}": float(d)
        for (a, b), d in engine.xi_distance_memory.items()
    }
    xi_clusters = engine.xi_clusters(inter)
    xi_cluster_sizes = {}
    for v, cid in xi_clusters.items():
        xi_cluster_sizes[cid] = xi_cluster_sizes.get(cid, 0) + 1
        
    # --------------------------------
    # Sanity check (DEBUG ONLY)
    # --------------------------------
    if engine.time % 100 == 0:
        print(
            f"[geom-check] t={engine.time} "
            f"topo_pairs={len(topo_geometry)} "
            f"xi_pairs={len(xi_geometry)} "
            f"xi_clusters={len(xi_cluster_sizes)}"
        )
    
    # ---------------------------
    # Log interaction snapshot
    # ---------------------------
    t2 = time.perf_counter()
    interaction_log.append({
        "time": engine.time,
        "rewrite_accepted": accepted,

        # ξ geometry
        "xi_support": xi_support,
        "xi_num_clusters": len(xi_cluster_sizes),
        "xi_cluster_sizes": xi_cluster_sizes,

        "topo_geometry": topo_geometry,
        "xi_geometry": xi_geometry,
        
        "Omega": getattr(engine, "_cached_omega", None),  # 🔧 reuse cached omega if available
        "interaction_graph_size": len(inter),
    })
    t3 = time.perf_counter()
    if engine.time % 100 == 0:
        print(
            f"[perf] t={engine.time} "
            f"engine={(t1 - t0)*1000:.2f}ms "
            f"observer={(t3 - t2)*1000:.2f}ms "
            f"total={(t3 - t0)*1000:.2f}ms "
        )
# Save output
# -------------------------------
out = {
    "metadata": {
        "seed": SEED,
        "omega_target": OMEGA_TARGET,
        "interaction_steps": INTERACTION_STEPS,
        "first_injection_time": first_injection_time,
        "second_injection_time": second_injection_time,
    },
    "interaction_log": interaction_log,
}

with open("analysis/interaction_experiment.json", "w") as f:
    json.dump(out, f, indent=2)

print("Saved → analysis/interaction_experiment.json")