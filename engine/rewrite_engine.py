# engine/rewrite_engine.py

import random
import time
import math
from collections import defaultdict

from engine.rules import edge_creation_rule, vertex_fusion_rule
from engine.observables import (
    worldline_interaction_graph,
    interaction_concentration,
    closure_density,
    hierarchical_closure,
)
from engine.physics_params import GAMMA_DEFECT


# --------------------------------------------------
# Local Ω proxy
# --------------------------------------------------
def local_omega(H, inter, v):
    neighbors = inter.get(v, [])
    if not neighbors:
        return 0.0
    closed = 0
    for u in neighbors:
        if u in inter and v in inter[u]:
            closed += 1
    return closed / max(len(neighbors), 1)


# --------------------------------------------------
# Rewrite Engine
# --------------------------------------------------
class RewriteEngine:
    """
    Time + space emergence via inertia biases.
    Path A: propagating influence field ξ
    """

    def __init__(
        self,
        hypergraph,
        p_create=0.6,
        seed=None,
        gamma_time=0.1,
        gamma_ext=0.05,
        gamma_closure=0.05,
        gamma_hier=0.06,
        epsilon_label_violation=0.08,
        XI_DECAY=0.85,
        XI_COUPLING=0.6,
        verbose=True,
        print_interval=50,
    ):
        self.H = hypergraph
        self.p_create = p_create

        self.gamma_time = gamma_time
        self.gamma_ext = gamma_ext
        self.gamma_closure = gamma_closure
        self.gamma_hier = gamma_hier
        self.epsilon_label_violation = epsilon_label_violation

        # ξ field
        self.xi = {}
        self.prev_xi = {}
        self.xi_threshold = 1e-6
        self.XI_DECAY = XI_DECAY
        self.XI_COUPLING = XI_COUPLING

        # cluster + geometry memory
        self.topo_distance_memory = {}
        self.xi_distance_memory = {}
        self.DISTANCE_MEMORY_DECAY = 0.9
        self.geometry_stride = 5
        

        # logs
        self.rewrite_history = []
        self.xi_current_log = []
        self.defect_log = []

        # rewrite bookkeeping
        self.last_rewrite = None
        self.forced_time = None
        self.time = 0
        self.verbose = verbose
        self.print_interval = print_interval

        if seed is not None:
            random.seed(seed)

    # --------------------------------------------------
    # Main step
    # --------------------------------------------------
    def step(self):
        _t0 = time.perf_counter()
        self.prev_xi = dict(self.xi)

        # ---------------------------------
        # Reuse cached state
        # ---------------------------------
        if hasattr(self, "_cached_inter"):
            inter_before = self._cached_inter
            omega_before = self._cached_omega
        else:
            inter_before = worldline_interaction_graph(self.H)
            omega_before = hierarchical_closure(self.H, inter_before)

        # ---------------------------------
        # Propose rewrite
        # ---------------------------------
        undo = self._propose_rewrite()
        if undo is None:
            return False

        self.last_rewrite = {
            "added_vertices": undo.get("added_vertices", []),
            "removed_vertices": (
                [undo["removed_vertex"].id]
                if "removed_vertex" in undo else []
            ),
            "added_edges": undo.get("added_edges", []),
        }

        # ---------------------------------
        # Tentative interaction graph
        # ---------------------------------
        inter_after = worldline_interaction_graph(self.H)
        omega_after = hierarchical_closure(self.H, inter_after)
        delta_omega = omega_after - omega_before

        # ---------------------------------
        # Acceptance rule
        # ---------------------------------
        accept_prob = 1.0
        if abs(delta_omega) > self.epsilon_label_violation:
            V = len(self.H.vertices)
            gamma = GAMMA_DEFECT * math.exp(-V / 800)
            accept_prob *= math.exp(-gamma * abs(delta_omega))

        accepted = random.random() <= accept_prob

        if not accepted:
            self.undo_changes(undo)
            self._cached_inter = inter_before
            self._cached_omega = omega_before
            omega_print = omega_before

        else:
            # Cache accepted state
            self._cached_inter = inter_after
            self._cached_omega = omega_after
            omega_print = omega_after

            # -----------------------------
            # ξ inheritance
            # -----------------------------
            parents = [
                v for v in self.touched_vertices()
                if v in self.xi and self.xi[v] > self.xi_threshold
            ]
            for vid in self.last_rewrite["added_vertices"]:
                if parents:
                    inherited = sum(self.xi[p] for p in parents) / len(parents)
                    self.xi[vid] = self.xi.get(vid, 0.0) + 0.5 * inherited

            # -----------------------------
            # ξ propagation
            # -----------------------------
            xi_clusters = self.xi_clusters(inter_after)
            self._propagate_xi(inter_after, xi_clusters)
            

            # -----------------------------
            # Geometry updates - matter defined
            # -----------------------------
            if self.time % self.geometry_stride == 0:
                # ξ must exist to define geometry
                xi_support = {
                    v for v, x in self.xi.items()
                    if x > self.xi_threshold and math.isfinite(x)
                }
                
                if len(xi_support) >= 2:
                    # --- topo geometry restricted to xi_support ---
                    topo = self.topo_clusters(inter_after)
                    
                    # group xi_support by topo component
                    topo_with_xi = defaultdict(list)
                    for v in xi_support:
                        topo_cid = topo.get(v)
                        if topo_cid is not None:
                            topo_with_xi[topo_cid].append(v)
                    
                    # update geometry inside each topo component
                    for _, verts in topo_with_xi.items():
                        if len(verts) < 2:
                            continue
                        
                        self._update_topo_distance_memory(
                            inter_after,
                            restrict_to=verts
                        )

                    # --- ξ geometry ---
                    if len(set(self.xi_clusters(inter_after).values())) >= 2:
                        self._update_xi_distance_memory(inter_after)

            # -----------------------------
            # Logs
            # -----------------------------
            self._record_rewrite(undo)
            self._record_xi_current(inter_after)

        # ---------------------------------
        # Timing + diagnostics
        # ---------------------------------
        self._last_step_time = time.perf_counter() - _t0
        self.time += 1
        
        if self.verbose and self.time % self.print_interval == 0:
            xi_count = sum(1 for x in self.xi.values() if x > self.xi_threshold)
            print(
                f"[engine] t={self.time} "
                f"step={self._last_step_time*1000:.2f}ms "
                f"Ω={omega_print:.6f} "
                f"|ξ|={xi_count} "
                f"geom_pairs={len(self.topo_distance_memory) + len(self.xi_distance_memory)}"
            )

        return accepted
    
    # --------------------------------------------------
    # Rewrite proposal
    # --------------------------------------------------
    def _propose_rewrite(self):
        protected_ids = [
            vid for vid, x in self.xi.items()
            if x > self.xi_threshold and vid in self.H.vertices
        ]
    
        if protected_ids and random.random() < 0.7:
            vid = random.choice(protected_ids)
            v_obj = self.H.vertices[vid]
            return edge_creation_rule(self.H, anchor_vertex=v_obj)
    
        if random.random() < 0.6:
            return edge_creation_rule(self.H)
    
        return vertex_fusion_rule(self.H)
    # --------------------------------------------------
    # ξ propagation (cluster-aware, ORIGINAL)
    # --------------------------------------------------
    def _propagate_xi(self, inter, clusters):
        new_xi = dict(self.xi)
        
        XI_MAX = 1e6

        for v, xi_v in self.xi.items():
            if xi_v < self.xi_threshold:
                continue

            cid_v = clusters.get(v)
            xi_v *= self.XI_DECAY

            neighbors = inter.get(v, [])
            deg = max(len(neighbors), 1)
            
            for u in neighbors:
                cid_u = clusters.get(u)
                if cid_u is not None and cid_v is not None and cid_u != cid_v:
                    continue

                new_xi[u] = new_xi.get(u, 0.0) + 0.5 * xi_v / deg

            new_xi[v] = new_xi.get(v, 0.0) + 0.5 * xi_v
            
        for v in new_xi:
            if new_xi[v] > XI_MAX:
                new_xi[v] = XI_MAX

        self.xi = new_xi
    

    # --------------------------------------------------
    # ξ clusters
    # --------------------------------------------------
    def xi_clusters(self, inter):
        clusters = {}
        visited = set()
        cid = 0

        xi_vertices = {
            v for v, x in self.xi.items()
            if x > self.xi_threshold and v in self.H.vertices
        }

        for v in xi_vertices:
            if v in visited:
                continue
            stack = [v]
            visited.add(v)
            clusters[v] = cid

            while stack:
                u = stack.pop()
                for w in inter.get(u, []):
                    if w in xi_vertices and w not in visited:
                        visited.add(w)
                        clusters[w] = cid
                        stack.append(w)
            cid += 1

        return clusters
    
    # --------------------------------------------------
    # Topological clusters (PURE TOPOLOGY)
    # --------------------------------------------------    
    def topo_clusters(self, inter):
        """
        Pure topological connected components.
        Geometry lives here.
        """
        clusters = {}
        visited = set()
        cid = 0

        for v in inter:
            if v in visited:
                continue
            stack = [v]
            visited.add(v)
            clusters[v] = cid

            while stack:
                u = stack.pop()
                for w in inter.get(u, []):
                    if w not in visited:
                        visited.add(w)
                        clusters[w] = cid
                        stack.append(w)
            cid += 1

        return clusters

    # --------------------------------------------------
    # Geometry memory (G1)
    # --------------------------------------------------
    def _update_topo_distance_memory(self, inter, restrict_to):
        topo = self.topo_clusters(inter)
        
        # group by topo id inside restrict_to
        topo_groups = defaultdict(list)
        for v in restrict_to:
            cid = topo.get(v)
            if cid is not None:
                topo_groups[cid].append(v)
        
        topo_ids = list(topo_groups.keys())
        if len(topo_ids) < 2:
            return

        for i in range(len(topo_ids)):
            for j in range(i + 1, len(topo_ids)):
                A = topo_groups[topo_ids[i]]
                B = set(topo_groups[topo_ids[j]])

                d = min(
                    self.graph_distance(inter, v, B, max_depth=6)
                    for v in A
                )
                if not math.isfinite(d):
                    continue

                key = ("topo", topo_ids[i], topo_ids[j])
                prev = self.topo_distance_memory.get(key, d)
                self.topo_distance_memory[key] = (
                    self.DISTANCE_MEMORY_DECAY * prev
                    + (1 - self.DISTANCE_MEMORY_DECAY) * d
                )

    # --------------------------------------------------
    # Cluster distance memory (G2)
    # --------------------------------------------------
    def _update_xi_distance_memory(self, inter):
        """
        OPTION 1:
        ξ-geometry only exists when ξ clusters
        live inside the SAME topo component.
        """

        topo = self.topo_clusters(inter)
        xi_clusters = self.xi_clusters(inter)

        # (topo_component, xi_cluster) → vertices
        bucket = defaultdict(list)

        for v, xi_cid in xi_clusters.items():
            topo_cid = topo.get(v)
            if topo_cid is None:
                continue
            bucket[(topo_cid, xi_cid)].append(v)

        # group by topo component
        topo_groups = defaultdict(dict)
        for (topo_cid, xi_cid), verts in bucket.items():
            topo_groups[topo_cid][xi_cid] = verts

        # compute geometry ONLY inside same topo component
        for topo_cid, xi_groups in topo_groups.items():
            xi_ids = list(xi_groups.keys())
            if len(xi_ids) < 2:
                continue

            for i in range(len(xi_ids)):
                for j in range(i + 1, len(xi_ids)):
                    A = xi_groups[xi_ids[i]]
                    B = set(xi_groups[xi_ids[j]])

                    d = min(
                        self.graph_distance(inter, v, B, max_depth=6)
                        for v in A
                    )

                    if not math.isfinite(d):
                        continue

                    key = ("xi", xi_ids[i], xi_ids[j])
                    prev = self.xi_distance_memory.get(key, d)

                    self.xi_distance_memory[key] = (
                        self.DISTANCE_MEMORY_DECAY * prev
                        + (1 - self.DISTANCE_MEMORY_DECAY) * d
                    )
    # --------------------------------------------------
    # ξ-current logging
    # --------------------------------------------------
    def _record_xi_current(self, inter):
        touched = self.touched_vertices()
        delta_xi = {}
        for v in touched:
            if v in self.prev_xi:
                delta = self.xi.get(v, 0.0) - self.prev_xi.get(v, 0.0)
                if math.isfinite(delta):
                    delta_xi[v] = delta

        if delta_xi:
            self.xi_current_log.append({
                "time": self.time,
                "delta_xi": delta_xi,
            })

    # --------------------------------------------------
    # Utilities
    # --------------------------------------------------
    def touched_vertices(self):
        if self.last_rewrite is None:
            return set()
        return set(
            self.last_rewrite["added_vertices"]
            + self.last_rewrite["removed_vertices"]
        )

    def graph_distance(self, inter, start, targets, max_depth=50):
        if start in targets:
            return 0
        visited = {start}
        frontier = {start}
        depth = 0

        while frontier and depth < max_depth:
            depth += 1
            nxt = set()
            for v in frontier:
                for u in inter.get(v, []):
                    if u in visited:
                        continue
                    if u in targets:
                        return depth
                    visited.add(u)
                    nxt.add(u)
            frontier = nxt
        return float("inf")

    def _record_rewrite(self, undo):
        self.rewrite_history.append({
            "time": self.time,
            "rewrite": undo,
        })
        
    def _vid_to_vertex(self, vid):
        return self.H.vertices.get(vid)
        
    # --------------------------------------------------
    # Export geometry (JSON-safe)
    # --------------------------------------------------
    def export_cluster_geometry(self):
        """
        Export both topo and ξ geometries.
        """
        return {
            "topo": {
                f"{a},{b}": float(d)
                for (a, b), d in self.topo_distance_memory.items()
                if math.isfinite(d)
            },
            "xi": {
                f"{a},{b}": float(d)
                for (a, b), d in self.xi_distance_memory.items()
                if math.isfinite(d)
            },
        }
        
    # --------------------------------------------------
    # Forced probes (matter injection)
    # --------------------------------------------------
    def force_defect(self, magnitude):
        vid = random.choice(list(self.H.vertices.keys()))
        v_obj = self._vid_to_vertex(vid)
        undo = edge_creation_rule(self.H, anchor_vertex=v_obj)
        if undo is None:
            return False

        self.xi[vid] = self.xi.get(vid, 0.0) + magnitude
        self.forced_time = self.time
        self._record_rewrite(undo)
        
        if self.verbose:
            print(f"[inject] defect at t={self.time} v={vid}")
        return True

    def force_second_proto_object(self, omega_kick, xi_seed, min_distance):
        inter = worldline_interaction_graph(self.H)
        xi_support = {vid for vid, x in self.xi.items() if x > self.xi_threshold}
        if not xi_support:
            return False

        best_vid = None
        best_d = -1

        for vid in self.H.vertices.keys():
            d = self.graph_distance(inter, vid, xi_support, max_depth=20)
            if d > best_d:
                best_d = d
                best_vid = vid

            if d >= min_distance:
                self.xi[vid] = xi_seed
                # 🔧 FORCE causal bridge (DEBUG ONLY)
                u = next(iter(xi_support))
                self.H.add_causal_relation(
                    self.H.vertices[u],
                    self.H.vertices[vid],
                )
                self.forced_time = self.time
                print(
                    f"### SECOND PROBE at t={self.time} | v={vid} | d={d}"
                )
                return True

        # fallback
        if best_vid is not None and best_d > 0:
            self.xi[best_vid] = xi_seed
            self.forced_time = self.time
            print(
                f"### SECOND PROBE (fallback) at t={self.time} | "
                f"v={best_vid} | max_d={best_d}"
            )
            return True

        return False

    def undo_changes(self, undo):
        if "removed_vertex" in undo:
            v = undo["removed_vertex"]
            self.H.vertices[v.id] = v
            self.H.causal_order[v.id] = set()

        for eid, e in undo.get("removed_edges", {}).items():
            self.H.hyperedges[eid] = e

        for eid in undo.get("added_edges", []):
            self.H.hyperedges.pop(eid, None)

        for vid in undo.get("added_vertices", []):
            self.H.vertices.pop(vid, None)
            self.H.causal_order.pop(vid, None)