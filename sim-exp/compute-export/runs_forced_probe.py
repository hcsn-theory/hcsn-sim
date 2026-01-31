import json
import random
from engine.hypergraph import Hypergraph
from engine.rewrite_engine import RewriteEngine
from engine.observables import hierarchical_closure, worldline_interaction_graph
from engine.rules import edge_creation_rule

TARGETS = {
    "critical": 1.10,
}

TOL = 0.05
MAX_STEPS = 20000

# NEW: split post steps
STABILIZE_STEPS = 1200
INTERACTION_STEPS = 5000

for label, Omega_target in TARGETS.items():
    print(f"\n=== Running forced probe: {label} ===")

    # --- initialize ---
    H = Hypergraph()
    v1 = H.add_vertex()
    v2 = H.add_vertex()
    H.add_causal_relation(v1, v2)
    H.add_hyperedge([v1, v2])

    engine = RewriteEngine(H, seed=1)

    probe_time = None
    probe_vertex = None

    # --- evolve until target Ω ---
    for _ in range(MAX_STEPS):
        engine.step()

        inter = worldline_interaction_graph(H)
        Omega = hierarchical_closure(H, inter)

        if abs(Omega - Omega_target) < TOL:
            probe_time = engine.time

            # --- FIRST FORCED PROBE ---
            success = engine.force_defect(magnitude=0.3)
            if not success:
                print("⚠ Forced probe failed")
            else:
                probe_vertex = engine.defect_log[-1].get("anchor_vertex")
                print(
                    f"### FORCED PROBE at t={engine.time} | "
                    f"Ω={Omega:.3f} | v={probe_vertex}"
                )
            break

    if probe_time is None:
        print("⚠ Did not reach target Ω - forcing at early time")
        engine.force_defect(magnitude=0.3)
        probe_time = engine.time

    # -------------------------------------------------
    # NEW PART 1: let first proto-particle stabilize
    # -------------------------------------------------
    for _ in range(STABILIZE_STEPS):
        engine.step()

    # -------------------------------------------------
    # NEW PART 2: inject second proto-object
    # -------------------------------------------------
    success = engine.force_second_proto_object(
        omega_kick=0.3,
        xi_seed=1.0,
        min_distance=15,
    )

    if not success:
        print("⚠ Second proto-object injection failed")

    # -------------------------------------------------
    # NEW PART 3: observe interaction
    # -------------------------------------------------
    for _ in range(INTERACTION_STEPS):
        engine.step()

    # --- save ---
    out = {
        "regime": label,
        "Omega_target": Omega_target,
        "probe_time": probe_time,
        "probe_vertex": probe_vertex,
        "defects": engine.defect_log,
        "rewrite_history": engine.rewrite_history,
    }

    fname = f"analysis/forced_probe_{label}.json"
    with open(fname, "w") as f:
        json.dump(out, f, indent=2)

    print(f"Saved → {fname}")