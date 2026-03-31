import json
import os
import time

from engine.hypergraph import Hypergraph
from engine.rewrite_engine import RewriteEngine
from engine.observables import worldline_interaction_graph, hierarchical_closure

STABILIZE_STEPS_BEFORE_PROBE = 150
INTERACTION_STEPS = 1500
OMEGA_TARGET = 1.10
OMEGA_TOL = 0.05
SEED = 1


def main():
    H = Hypergraph()
    v1 = H.add_vertex()
    v2 = H.add_vertex()
    H.add_causal_relation(v1, v2)
    H.add_hyperedge([v1, v2])

    engine = RewriteEngine(H, p_create=0.6, seed=SEED)

    while True:
        engine.step()
        inter = worldline_interaction_graph(H, fraction=0.0)
        omega = hierarchical_closure(H, inter)
        if abs(omega - OMEGA_TARGET) < OMEGA_TOL:
            break

    ok = engine.force_defect(magnitude=0.3, max_tries=30)
    if not ok:
        print("[warn] First proto-particle injection failed — continuing anyway")

    first_injection_time = engine.time

    for _ in range(STABILIZE_STEPS_BEFORE_PROBE):
        engine.step()

    if not engine.xi:
        seed_v = next(iter(engine.H.vertices.keys()))
        engine.xi[seed_v] = 0.2
        print(f"[inject] re-seeded xi at v={seed_v}")

    ok = engine.force_second_proto_object(
        omega_kick=0.3,
        xi_seed=1.0,
        min_distance=6,
        max_tries=50,
    )
    if not ok:
        print("[warn] Second proto-particle injection failed — continuing experiment")

    second_injection_time = engine.time

    interaction_log = []

    for _ in range(INTERACTION_STEPS):
        t0 = time.perf_counter()
        engine.step()

        if engine.time % 200 == 0:
            print(
                f"[geom-live] topo={len(engine.topo_distance_memory)} "
                f"xi={len(engine.xi_distance_memory)}"
            )

        t1 = time.perf_counter()
        inter = worldline_interaction_graph(H, fraction=0.0)

        xi_count = sum(
            1 for x in engine.xi.values()
            if x > engine.xi_threshold
        )

        omega = hierarchical_closure(H, inter)

        interaction_log.append({
            "t": engine.time,
            "Ω": round(float(omega), 6),
            "xi": {
                "count": xi_count,
            },
            "geometry": {
                "topo_pairs": len(engine.topo_distance_memory),
                "xi_pairs": len(engine.xi_distance_memory),
            },
            "graph": {
                "vertices": len(engine.H.vertices),
                "hyperedges": len(engine.H.hyperedges),
                "interaction_nodes": len(inter),
            },
        })

        t2 = time.perf_counter()
        if engine.time % 100 == 0:
            print(
                f"[perf] t={engine.time} "
                f"engine={(t1 - t0)*1000:.2f}ms "
                f"observer={(t2 - t1)*1000:.2f}ms "
                f"total={(t2 - t0)*1000:.2f}ms"
            )

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

    os.makedirs("exports", exist_ok=True)
    with open("exports/interaction_experiment.json", "w") as f:
        json.dump(out, f, indent=2)

    print("Saved -> exports/interaction_experiment.json")


if __name__ == "__main__":
    main()
