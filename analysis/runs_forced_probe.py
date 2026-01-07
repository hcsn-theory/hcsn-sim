import json
import random
from engine.hypergraph import Hypergraph
from engine.rewrite_engine import RewriteEngine
from engine.observables import hierarchical_closure, worldline_interaction_graph
from engine.rules import edge_creation_rule

TARGETS = {
    "subcritical": 0.65,
    "critical": 1.10,
    "supercritical": 1.45,
}

TOL = 0.05
MAX_STEPS = 8000
POST_STEPS = 3000

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

            # --- FORCED PROBE ---
            success = engine.force_defect(magnitude=0.3)
            if not success:
                print("⚠ Forced probe failed")
            else:
                probe_vertex = engine.defect_log[-1].get("anchor_vertex")
                print(
                    f"### FORCED PROBE at t={engine.time} | "
                    f"Ω={Omega:.3f} | v={probe_vertex}"
                )
            break   # ← IMPORTANT: stop searching once probe is injected
    
    if probe_time is None:
        print("⚠ Did not reach target Ω - forcing at early time")
        engine.force_defect(magnitude=0.3)
        probe_time = engine.time

    # --- post-probe evolution ---
    for _ in range(POST_STEPS):
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