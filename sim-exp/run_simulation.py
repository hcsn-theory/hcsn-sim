import argparse
import json
import os
import time

from engine.hypergraph import Hypergraph
from engine.rewrite_engine import RewriteEngine
from engine.observables import worldline_interaction_graph, hierarchical_closure


def save_data(engine, config):
    print("\nExporting final datasets...")

    tau_c = 1000
    lifetimes = []

    for k in engine.dead_knots:
        if k.age < 50:
            continue

        is_particle = (k.age >= tau_c and k.coherence > 1.0)
        mean_stab = (
            sum(engine.stability.get(v, 0.0) for v in k.vertices) / max(len(k.vertices), 1)
        )

        lifetimes.append({
            "id": k.id,
            "status": "dead",
            "age": k.age,
            "max_size": k.max_size,
            "radius": k.radius,
            "coherence": k.coherence,
            "velocity": k.velocity,
            "velocity_avg": k.velocity_avg,
            "mass": k.mass,
            "momentum": k.momentum,
            "worldline_length": len(k.position_history),
            "particle_candidate": is_particle,
            "mean_stability": mean_stab,
        })

    for k in engine.active_knots.values():
        if k.age < 50:
            continue

        is_particle = (k.age >= tau_c and k.coherence > 1.0)
        mean_stab = (
            sum(engine.stability.get(v, 0.0) for v in k.vertices) / max(len(k.vertices), 1)
        )

        lifetimes.append({
            "id": k.id,
            "status": "alive",
            "age": k.age,
            "max_size": k.max_size,
            "radius": k.radius,
            "coherence": k.coherence,
            "velocity": k.velocity,
            "velocity_avg": k.velocity_avg,
            "mass": k.mass,
            "momentum": k.momentum,
            "worldline_length": len(k.position_history),
            "particle_candidate": is_particle,
            "mean_stability": mean_stab,
        })

    os.makedirs("exports", exist_ok=True)

    out_file = f"exports/particle_lifetimes_p{config.p_create:.2f}_s{config.seed}.json"
    with open(out_file, "w") as f:
        json.dump(lifetimes, f, indent=2)

    out_ev = f"exports/interaction_events_p{config.p_create:.2f}_s{config.seed}.json"
    with open(out_ev, "w") as f:
        json.dump([ev.to_dict() for ev in engine.interaction_events], f, indent=2)

    particle_count = sum(1 for p in lifetimes if p["particle_candidate"])
    print(f"Exported {len(engine.interaction_events)} interaction events to {out_ev}")
    print(
        f"Exported {len(lifetimes)} worldlines "
        f"({particle_count} candidates >= {tau_c}) to {out_file}"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=5000)
    parser.add_argument("--p_create", type=float, default=0.60)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--sample_interval", type=int, default=1000)
    parser.add_argument("--noise_bias", type=float, default=0.0)
    parser.add_argument("--defect_injection", type=float, default=0.0)
    parser.add_argument("--geometry_freeze", type=float, default=0.9)
    config = parser.parse_args()

    print("\n" + "=" * 86)
    print(f"RUN STARTED (Python Engine) | Seed: {config.seed} | Steps: {config.steps}")
    print("=" * 86)

    H = Hypergraph()
    v1 = H.add_vertex()
    v2 = H.add_vertex()
    H.add_causal_relation(v1, v2)
    H.add_hyperedge([v1, v2])

    engine = RewriteEngine(H, p_create=config.p_create, seed=config.seed)
    engine.params.noise_bias = config.noise_bias
    engine.params.defect_injection = config.defect_injection
    engine.DISTANCE_MEMORY_DECAY = config.geometry_freeze
    engine.verbose = False

    accepted = 0
    rejected = 0
    last_k = H.average_coordination()
    last_L = H.max_chain_length()
    last_omega = 0.0

    start_time = time.time()
    last_print_time = time.time()

    print(" time  |   V   |  <k>  | Δ<k> |  L  | ΔL | acc%   | omega | knots | all_k | max_coh | step_ms")

    for _ in range(1, config.steps + 1):
        success = engine.step()
        if success:
            accepted += 1
        else:
            rejected += 1

        if engine.time % config.sample_interval != 0:
            continue

        inter = worldline_interaction_graph(H, fraction=0.0)
        k = H.average_coordination()
        L = H.max_chain_length()
        dk = k - last_k
        dL = L - last_L

        omega = hierarchical_closure(H, inter)
        total_attempts = accepted + rejected
        acc_ratio = (accepted / total_attempts) if total_attempts > 0 else 0.0

        valid_knots = sum(1 for knot in engine.active_knots.values() if knot.age >= 50 and knot.radius < 5.0)
        total_knots = len(engine.active_knots)

        max_coh = 0.0
        for v in H.vertices.keys():
            neighbors = inter.get(v)
            if not neighbors:
                continue
            neighborhood = set(neighbors)
            neighborhood.add(v)
            ie = 0
            be = 0
            for n in neighborhood:
                for nn in inter.get(n, set()):
                    if nn in neighborhood:
                        ie += 1
                    else:
                        be += 1
            ie //= 2
            coh = (ie / be) if be > 0 else (10.0 if ie > 0 else 0.0)
            if coh > max_coh:
                max_coh = coh

        now = time.time()
        step_ms = int((now - last_print_time) * 1000)
        last_print_time = now

        print(
            f"{engine.time:6d} | {len(H.vertices):5d} | {k:5.2f} | {dk:+5.2f} | "
            f"{L:3d} | {dL:+3d} | {acc_ratio*100:5.1f}% | {omega:5.3f} | "
            f"{valid_knots:5d} | {total_knots:5d} | {max_coh:7.3f} | {step_ms:7d}"
        )

        last_k = k
        last_L = L
        last_omega = omega

    end_time = time.time() - start_time
    print(f"\nSimulation loop ended. Wall time: {end_time:.2f} s")

    save_data(engine, config)

    print("\n" + "=" * 86)
    print("FINISHED")


if __name__ == "__main__":
    main()
