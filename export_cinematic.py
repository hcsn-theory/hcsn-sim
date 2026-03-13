#!/usr/bin/env python3
"""
HCSN Cinematic Exporter
-----------------------
Runs the HCSN rewrite engine offline and computes continuous 3D force-directed 
physics coordinates for all vertices and edges over time.
Saves the output as a timeline JSON file that can be imported directly into 
Blender, Maya, or Unreal Engine to render high-quality glowing node structures.
"""

import sys
import os
import math
import json
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.hypergraph import Hypergraph
from engine.rewrite_engine import RewriteEngine
from engine.observables import worldline_interaction_graph, hierarchical_closure

# ── Export Settings ─────────────────────────────────────
TOTAL_FRAMES = 500
STEPS_PER_FRAME = 3
EXPORT_FILE = "cinematic_frames.json"

# ── Physics Constants ─────────────────────────────────
REPEL = 90.0
ATTRACT = 0.032
DAMP = 0.60
Z_FORCE = 0.06
GRAVITY = 0.022
MAX_VEL = 3.0

class ForceLayout3D:
    def __init__(self):
        self.positions = {}
        self.velocities = {}

    def get_pos(self, vid, depth):
        if vid not in self.positions:
            # Spawn new nodes
            spread = 30.0
            r_z = float(depth) * 5.0
            x = (random.random() - 0.5) * spread
            y = (random.random() - 0.5) * spread
            z = r_z + (random.random() - 0.5) * spread * 0.2
            self.positions[vid] = [x, y, z]
            self.velocities[vid] = [0.0, 0.0, 0.0]
        return self.positions[vid]

    def apply_forces(self, active_vids, edges, depths):
        n = len(active_vids)
        if n == 0: return

        # Read positions/velocities into temporary arrays
        px, py, pz = [], [], []
        vx, vy, vz = [], [], []
        
        for vid in active_vids:
            p = self.get_pos(vid, depths[vid])
            v = self.velocities[vid]
            px.append(p[0])
            py.append(p[1])
            pz.append(p[2])
            vx.append(v[0])
            vy.append(v[1])
            vz.append(v[2])

        # Optimize by slicing a maximum sample for repulsion
        sample_size = min(n, 100)
        
        # Repulsion
        for i in range(sample_size):
            for j in range(i + 1, sample_size):
                dx = px[i] - px[j]
                dy = py[i] - py[j]
                dz = pz[i] - pz[j]
                d2 = max(dx*dx + dy*dy + dz*dz, 0.25)
                f = REPEL / d2
                dist = math.sqrt(d2)
                il = f / dist
                fx, fy, fz = dx*il, dy*il, dz*il
                
                vx[i] += fx; vy[i] += fy; vz[i] += fz
                vx[j] -= fx; vy[j] -= fy; vz[j] -= fz

        # Attraction
        vid_to_idx = {vid: idx for idx, vid in enumerate(active_vids)}
        for edge in edges:
            for i in range(len(edge) - 1):
                ida, idb = edge[i], edge[i+1]
                idx_a, idx_b = vid_to_idx.get(ida), vid_to_idx.get(idb)
                if idx_a is not None and idx_b is not None:
                    dx = px[idx_b] - px[idx_a]
                    dy = py[idx_b] - py[idx_a]
                    dz = pz[idx_b] - pz[idx_a]
                    
                    fx, fy, fz = dx*ATTRACT, dy*ATTRACT, dz*ATTRACT
                    vx[idx_a] += fx; vy[idx_a] += fy; vz[idx_a] += fz
                    vx[idx_b] -= fx; vy[idx_b] -= fy; vz[idx_b] -= fz

        # Update and Gravity
        max_depth = max(depths.values()) if depths else 1
        for i, vid in enumerate(active_vids):
            # Center gravity
            dist = math.sqrt(px[i]**2 + py[i]**2)
            if dist > 0:
                vx[i] -= (px[i]/dist) * GRAVITY * dist
                vy[i] -= (py[i]/dist) * GRAVITY * dist
            
            # Z alignment
            target_z = (depths[vid] - max_depth/2.0) * 10.0
            vz[i] += (target_z - pz[i]) * Z_FORCE

            vx[i] *= DAMP
            vy[i] *= DAMP
            vz[i] *= DAMP

            # Speed Limit
            speed2 = vx[i]**2 + vy[i]**2 + vz[i]**2
            if speed2 > MAX_VEL**2:
                scale = MAX_VEL / math.sqrt(speed2)
                vx[i] *= scale; vy[i] *= scale; vz[i] *= scale

            px[i] += vx[i]
            py[i] += vy[i]
            pz[i] += vz[i]

            self.positions[vid] = [px[i], py[i], pz[i]]
            self.velocities[vid] = [vx[i], vy[i], vz[i]]


def main():
    print("=" * 54)
    print("  HCSN Cinematic Sequence Exporter")
    print("=" * 54)
    
    H = Hypergraph()
    v1 = H.add_vertex()
    v2 = H.add_vertex()
    H.add_causal_relation(v1, v2)
    H.add_hyperedge([v1, v2])

    engine = RewriteEngine(H, seed=1, XI_DECAY=0.70, verbose=False, print_interval=99999)
    layout = ForceLayout3D()
    
    frames = []

    for frame in range(TOTAL_FRAMES):
        # Step simulation
        for _ in range(STEPS_PER_FRAME):
            engine.step()

            # Autoinject proto particles to make an interesting animation
            if engine.time == 100:
                engine.force_defect(magnitude=0.3)
            elif engine.time == 300:
                engine.force_second_proto_object(omega_kick=0.3, xi_seed=1.0, min_distance=2)
            elif len(engine.xi) == 0:
                seed_v = next(iter(engine.H.vertices.keys()), None)
                if seed_v: engine.xi[seed_v] = 0.2

        # Extract rendering frame
        inter = getattr(engine, "_cached_inter", {})
        xi_cl = engine.xi_clusters(inter)
        
        active_verts = [v for v in H.vertices.values() if engine.xi.get(v.id, 0.0) > engine.xi_threshold]
        active_ids = {v.id for v in active_verts}
        
        edges_out = []
        for e in H.hyperedges.values():
            vids = [v.id for v in e.vertices]
            if len(vids) >= 2 and all(vid in active_ids for vid in vids):
                edges_out.append(vids)

        depths = {v.id: v.depth for v in active_verts}
        
        # Advance layout simulation
        for _ in range(3): # Multiple physical subsamples for rapid settling
             layout.apply_forces(list(active_ids), edges_out, depths)

        frame_data = {
            "time": engine.time,
            "vertices": [
                {
                    "id": v.id,
                    "pos": [round(c, 4) for c in layout.positions[v.id]],
                    "xi": round(engine.xi.get(v.id, 0.0), 4),
                    "cluster": xi_cl.get(v.id, -1)
                }
                for v in active_verts
            ],
            "edges": edges_out
        }
        frames.append(frame_data)
        
        sys.stdout.write(f"\\rExporting Frame [{frame+1}/{TOTAL_FRAMES}] ...")
        sys.stdout.flush()

    # Write out data
    print(f"\\nSaving {len(frames)} frames to {EXPORT_FILE}...")
    with open(EXPORT_FILE, "w") as f:
        json.dump(frames, f, separators=(',', ':'))
        
    print("Done! You can now load this JSON sequence into Blender via a Python importer.")

if __name__ == "__main__":
    main()
