"""
HCSN Live Visualizer Server  —  Interaction Experiment Mode
------------------------------------------------------------
Runs the full interaction experiment:
  Phase 0 : grow universe until Ω reaches target
  Phase 1 : inject first proto-particle (defect)
  Phase 2 : stabilise, then inject second proto-particle
  Phase 3 : observe interaction indefinitely

Run from root of hcsn-sim repo:
    python3 visualizer_server.py

Then open visualizer.html in your browser.
"""

import asyncio
import websockets
import json
import math
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.hypergraph import Hypergraph
from engine.rewrite_engine import RewriteEngine
from engine.observables import worldline_interaction_graph, hierarchical_closure

# ── Experiment parameters (mirrors interaction_experiment.py) ──
OMEGA_TARGET              = 1.10
OMEGA_TOL                 = 0.05
STABILIZE_BEFORE_PROBE    = 80
FIRST_DEFECT_MAG          = 0.3
SECOND_DEFECT_XI          = 1.0
SECOND_DEFECT_MIN_DIST    = 2     # lowered: xi is everywhere, distance 6 never reachable
SEED                      = 1

# ── Streaming ─────────────────────────────────────────────────
MAX_VERTICES = 350
MAX_EDGES    = 700
STREAM_HZ    = 15

# ── Phase labels ──────────────────────────────────────────────
PHASE_LABELS = {
    0: "GROWING  —  waiting for Omega target",
    1: "PARTICLE 1 INJECTED  —  stabilising",
    2: "PARTICLE 2 INJECTED  —  observing interaction",
}


def build_state(engine, H, phase):
    inter      = getattr(engine, "_cached_inter", {})
    xi_cl      = engine.xi_clusters(inter)
    xi_thresh  = engine.xi_threshold

    all_verts  = list(H.vertices.values())
    active     = [v for v in all_verts if engine.xi.get(v.id, 0.0) > xi_thresh]
    inactive   = [v for v in all_verts if engine.xi.get(v.id, 0.0) <= xi_thresh]

    send_verts = active[:]
    remaining  = MAX_VERTICES - len(send_verts)
    if remaining > 0:
        send_verts += inactive[-remaining:]

    send_ids   = {v.id for v in send_verts}

    edges_out  = []
    for e in H.hyperedges.values():
        vids = [v.id for v in e.vertices]
        if len(vids) >= 2 and all(vid in send_ids for vid in vids):
            edges_out.append(vids)
        if len(edges_out) >= MAX_EDGES:
            break

    xi_vals = [engine.xi.get(v.id, 0.0) for v in send_verts]
    xi_max  = max(xi_vals) if xi_vals else 1.0
    if not math.isfinite(xi_max) or xi_max == 0:
        xi_max = 1.0

    xi_count = sum(1 for x in engine.xi.values()
                   if x > xi_thresh and math.isfinite(x))

    cluster_sizes = {}
    for cid in xi_cl.values():
        cluster_sizes[cid] = cluster_sizes.get(cid, 0) + 1

    return {
        "t":          engine.time,
        "phase":      phase,
        "phase_label": PHASE_LABELS.get(phase, ""),
        "omega":      round(float(getattr(engine, "_cached_omega", 0.0)), 6),
        "xi_max":     round(float(xi_max), 6),
        "vertices": [
            {
                "id":      v.id,
                "depth":   v.depth,
                "label":   getattr(v, "label", 0),
                "xi":      round(float(engine.xi.get(v.id, 0.0)), 6),
                "cluster": xi_cl.get(v.id, -1),
            }
            for v in send_verts
        ],
        "edges": edges_out,
        "stats": {
            "total_vertices":  len(H.vertices),
            "total_edges":     len(H.hyperedges),
            "xi_count":        xi_count,
            "xi_clusters":     len(cluster_sizes),
            "largest_cluster": max(cluster_sizes.values(), default=0),
        },
    }


async def run_simulation(websocket, path=None):
    addr = getattr(websocket, "remote_address", "unknown")
    print(f"[server] Client connected: {addr}")

    H  = Hypergraph()
    v1 = H.add_vertex()
    v2 = H.add_vertex()
    H.add_causal_relation(v1, v2)
    H.add_hyperedge([v1, v2])

    engine = RewriteEngine(H, seed=SEED, XI_DECAY=0.70, verbose=False, print_interval=99999)
    engine.topo_distance_memory = {}
    engine.xi_distance_memory   = {}

    phase              = 0
    steps_since_inject = 0
    delay              = 1.0 / STREAM_HZ

    print("[server] Phase 0: growing universe toward Omega target...")

    try:
        while True:
            engine.step()

            if phase == 0:
                inter = worldline_interaction_graph(H)
                omega = hierarchical_closure(H, inter)
                if abs(omega - OMEGA_TARGET) < OMEGA_TOL:
                    print(f"[server] Omega={omega:.4f} reached at t={engine.time}")
                    ok = engine.force_defect(magnitude=FIRST_DEFECT_MAG)
                    if ok:
                        print(f"[server] Phase 1: first particle injected at t={engine.time}")
                        phase              = 1
                        steps_since_inject = 0
                    else:
                        print("[server] First inject failed, retrying next step")

            elif phase == 1:
                steps_since_inject += 1

                if not engine.xi:
                    seed_v = next(iter(engine.H.vertices.keys()), None)
                    if seed_v:
                        engine.xi[seed_v] = 0.2
                        print(f"[server] xi re-seeded at v={seed_v}")

                if steps_since_inject >= STABILIZE_BEFORE_PROBE:
                    ok = engine.force_second_proto_object(
                        omega_kick=0.3,
                        xi_seed=SECOND_DEFECT_XI,
                        min_distance=SECOND_DEFECT_MIN_DIST,
                    )
                    if ok:
                        print(f"[server] Phase 2: second particle injected at t={engine.time}")
                        phase = 2
                    else:
                        # Don't retry forever — force inject on a random inactive vertex
                        print(f"[server] Injection failed at t={engine.time}, forcing on random vertex")
                        candidates = [
                            vid for vid in engine.H.vertices
                            if engine.xi.get(vid, 0.0) <= engine.xi_threshold
                        ]
                        if candidates:
                            import random
                            vid = random.choice(candidates)
                            engine.xi[vid] = SECOND_DEFECT_XI
                            engine.forced_time = engine.time
                            print(f"[server] Force-injected at v={vid}")
                        phase = 2  # advance regardless

            state = build_state(engine, H, phase)
            try:
                await websocket.send(json.dumps(state))
            except (websockets.exceptions.ConnectionClosed,
                    websockets.exceptions.ConnectionClosedOK,
                    websockets.exceptions.ConnectionClosedError):
                break

            await asyncio.sleep(delay)

    except Exception as exc:
        print(f"[server] Error: {exc}")
        import traceback
        traceback.print_exc()
    finally:
        print(f"[server] Client disconnected: {addr}")


async def main():
    print("=" * 54)
    print("  HCSN Live Visualizer  -  Interaction Experiment")
    print("=" * 54)
    print(f"  WebSocket : ws://localhost:8765")
    print(f"  Stream    : {STREAM_HZ} fps  |  Seed: {SEED}")
    print(f"  Omega target : {OMEGA_TARGET} +/- {OMEGA_TOL}")
    print(f"  Open visualizer.html in your browser")
    print("=" * 54)

    async with websockets.serve(run_simulation, "localhost", 8765):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
