#!/usr/bin/env python3
"""
HCSN -> Depgraph CSV Exporter
Generates a streaming CSV of nodes and edges over time.
Columns: time, type, source, target, importance_xi, cluster
"""

import sys
import os
import csv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.hypergraph import Hypergraph
from engine.rewrite_engine import RewriteEngine

TOTAL_FRAMES = 250
EXPORT_FILE = "hcsn_sample.csv"

def main():
    print("=" * 54)
    print(" Generating HCSN CSV for Zackary's depgraph")
    print("=" * 54)
    
    H = Hypergraph()
    v1 = H.add_vertex()
    v2 = H.add_vertex()
    H.add_causal_relation(v1, v2)
    H.add_hyperedge([v1, v2])

    engine = RewriteEngine(H, seed=1, XI_DECAY=0.70, verbose=False, print_interval=99999)
    
    with open(EXPORT_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Header row
        writer.writerow(['t', 'type', 'source', 'target', 'importance_xi', 'cluster'])

        for frame in range(TOTAL_FRAMES):
            engine.step()

            # Inject proto-particles to make the data interesting for him
            if engine.time == 80:
                engine.force_defect(magnitude=0.3)
            elif engine.time == 150:
                engine.force_second_proto_object(omega_kick=0.3, xi_seed=1.0, min_distance=2)

            # Extract data
            inter = getattr(engine, "_cached_inter", {})
            xi_cl = engine.xi_clusters(inter)
            
            active_verts = [v for v in H.vertices.values() if engine.xi.get(v.id, 0.0) > engine.xi_threshold]
            active_ids = {v.id for v in active_verts}

            # 1. Write Nodes
            for v in active_verts:
                xi_val = round(engine.xi.get(v.id, 0.0), 4)
                cluster_id = xi_cl.get(v.id, -1)
                writer.writerow([engine.time, 'NODE', v.id, '', xi_val, cluster_id])

            # 2. Write Edges
            for e in H.hyperedges.values():
                vids = [v.id for v in e.vertices]
                if len(vids) >= 2 and all(vid in active_ids for vid in vids):
                    for i in range(len(vids) - 1):
                        writer.writerow([engine.time, 'EDGE', vids[i], vids[i+1], '', ''])
            
            sys.stdout.write(f"\rProcessing frame [{frame+1}/{TOTAL_FRAMES}] ...")
            sys.stdout.flush()

    print(f"\nDone! Saved to {EXPORT_FILE}.")

if __name__ == "__main__":
    main()
