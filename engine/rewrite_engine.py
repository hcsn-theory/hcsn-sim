# engine/rewrite_engine.py

import math
import random
import time
from collections import defaultdict

from engine.rules import edge_creation_rule, vertex_fusion_rule
from engine.observables import (
    worldline_interaction_graph,
    hierarchical_closure,
    detect_candidate_knots,
    component_radius,
    compute_coherence_raw,
    local_clustering,
    TopologicalKnot,
    InteractionEvent,
)
from engine.physics_params import PhysicsParams


class RewriteEngine:
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
        XI_DECAY=0.70,
        XI_COUPLING=0.6,
        verbose=True,
        print_interval=50,
        log_callback=None,
    ):
        self.H = hypergraph
        self.p_create = p_create

        self.gamma_time = gamma_time
        self.gamma_ext = gamma_ext
        self.gamma_closure = gamma_closure
        self.gamma_hier = gamma_hier
        self.epsilon_label_violation = epsilon_label_violation
        self.params = PhysicsParams()

        self.xi = {}
        self.prev_xi = {}
        self.xi_threshold = 1e-6
        self.XI_DECAY = XI_DECAY
        self.XI_COUPLING = XI_COUPLING

        self.topo_distance_memory = {}
        self.xi_distance_memory = {}
        self.DISTANCE_MEMORY_DECAY = 0.9
        self.geometry_stride = 5

        self.active_knots = {}
        self.next_knot_id = 1
        self.dead_knots = []
        self.interaction_events = []

        self.rewrite_history = []
        self.xi_current_log = []
        self.defect_log = []
        self.particle_activity = []

        self.last_rewrite = None
        self.forced_time = None
        self.time = 0
        self.verbose = verbose
        self.print_interval = print_interval
        self.log_callback = log_callback

        self._cached_inter = None
        self._cached_omega = None
        self.pending_bridge = None
        self.pending_bridge_time = None

        self._last_step_time = 0.0
        self.attempted_rewrites = 0
        self.suppressed_rewrites = 0

        self.stability = {}
        self.coupled_vertices = set()
        self.active_interactions = {}

        if seed is not None:
            random.seed(seed)

    def _log(self, msg):
        if self.log_callback:
            self.log_callback(msg)
        else:
            print(msg)

    def step(self):
        self.time += 1
        t0 = time.perf_counter()
        self.prev_xi = dict(self.xi)

        inter_before = (
            self._cached_inter
            if self._cached_inter is not None
            else worldline_interaction_graph(self.H, fraction=0.0)
        )
        omega_before = self._cached_omega if self._cached_omega is not None else 0.0

        if self.params.defect_injection > 0.0:
            if random.random() < self.params.defect_injection:
                v1 = self.H.add_vertex()
                v2 = self.H.add_vertex()
                v3 = self.H.add_vertex()
                v4 = self.H.add_vertex()
                nodes = [v1, v2, v3, v4]
                for i in range(4):
                    for j in range(i + 1, 4):
                        self.H.add_causal_relation(nodes[i], nodes[j])
                        self.H.add_hyperedge([nodes[i], nodes[j]])

        undo = self.propose_rewrite(inter_before)
        if undo is None and self.time % 200 == 0:
            if self.verbose:
                self._log(f"[debug] rewrite skipped at t = {self.time}")

        if undo is None:
            return False

        self.last_rewrite = {
            "added_vertices": list(undo.get("added_vertices", [])),
            "removed_vertex": undo.get("removed_vertex"),
            "kept_vertex": undo.get("kept_vertex"),
            "added_edges": [],
            "added_causal": [],
            "removed_edges": {},
            "old_causal": {},
        }

        inter_after = worldline_interaction_graph(self.H, fraction=0.0)

        if self.time % 200 == 0 and self.verbose:
            self._log(f"[debug] interaction nodes = {len(inter_after)}")

        omega_after = hierarchical_closure(self.H, inter_after) if self.time % 50 == 0 else omega_before
        delta_omega = omega_after - omega_before

        accept_prob = 1.0
        if abs(delta_omega) > self.epsilon_label_violation:
            V = len(self.H.vertices)
            gamma = self.params.gamma_defect * math.exp(-V / 800)
            accept_prob *= math.exp(-gamma * abs(delta_omega))

        if self.params.noise_bias > 0.0 and delta_omega > 0.0:
            accept_prob *= math.exp(self.params.noise_bias * delta_omega)
            accept_prob = min(1.0, accept_prob)

        accepted = random.random() <= accept_prob

        if not accepted:
            self.undo_changes(undo)
            self._cached_inter = inter_before
            self._cached_omega = omega_before
            omega_print = omega_before
        else:
            self._cached_inter = inter_after
            self._cached_omega = omega_after
            omega_print = omega_after

            touched = self.touched_vertices()
            parents = [p for p in touched if self.xi.get(p, 0.0) > self.xi_threshold]

            for vid in self.last_rewrite.get("added_vertices", []):
                if parents:
                    inherited = sum(self.xi[p] for p in parents) / len(parents)
                    self.xi[vid] = self.xi.get(vid, 0.0) + 0.5 * inherited

            xi_clusters = self.xi_clusters(inter_after)
            self.propagate_xi(inter_after, xi_clusters)

            geom_inter = inter_after

            if self.pending_bridge is not None and self.pending_bridge_time is not None:
                if self.time - self.pending_bridge_time >= 20:
                    u, v = self.pending_bridge
                    if u in self.H.vertices and v in self.H.vertices:
                        self.H.add_causal_relation(self.H.vertices[u], self.H.vertices[v])
                    self.pending_bridge = None
                    self.pending_bridge_time = None

            if self.time % self.geometry_stride == 0:
                xi_support = {
                    v for v, x in self.xi.items()
                    if x > self.xi_threshold and math.isfinite(x)
                }
                if len(xi_support) >= 2:
                    self.update_topo_distance_memory(geom_inter, xi_support)
                    self.update_xi_distance_memory(geom_inter)

            self.record_xi_current(geom_inter)

            if self.time % 10 == 0:
                self.update_topological_knots(geom_inter)
                self.update_stability(geom_inter)

        self._last_step_time = time.perf_counter() - t0

        if self.time % 200 == 0 and self.verbose:
            self._log(f"[debug] max causal depth = {self.H.max_chain_length()}")

        if self.verbose and self.time % self.print_interval == 0:
            valid_knots = sum(
                1 for k in self.active_knots.values()
                if k.age >= 50 and k.radius < 5.0
            )
            geom_pairs = len(self.topo_distance_memory) + len(self.xi_distance_memory)
            supp_ratio = (
                self.suppressed_rewrites / self.attempted_rewrites
                if self.attempted_rewrites > 0
                else 0.0
            )
            self._log(
                f"[engine] t={self.time} step={self._last_step_time*1000:.2f}ms "
                f"Ω={omega_print:.6f} knots={valid_knots} geom_pairs={geom_pairs} "
                f"supp_ratio={supp_ratio:.3f}"
            )
            self.attempted_rewrites = 0
            self.suppressed_rewrites = 0

        return accepted

    def update_topological_knots(self, inter):
        candidates = detect_candidate_knots(self.H, inter, min_coherence=1.2)
        next_active_knots = {}

        knot_pre_stats = {}
        for kid, knot in self.active_knots.items():
            stab = (
                sum(self.stability.get(v, 0.0) for v in knot.vertices)
                / max(len(knot.vertices), 1)
            )
            knot_pre_stats[kid] = (knot.coherence, len(knot.vertices), stab)

        matched_candidates = set()

        for _, knot in self.active_knots.items():
            best_idx = None
            best_overlap = 0.0

            for i, cand in enumerate(candidates):
                intersection = len(knot.vertices.intersection(cand))
                min_s = min(len(knot.vertices), len(cand))
                overlap = (intersection / min_s) if min_s > 0 else 0.0
                if overlap > 0.3 and overlap > best_overlap:
                    best_overlap = overlap
                    best_idx = i

            if best_idx is not None:
                matched_candidates.add(best_idx)
                cand = candidates[best_idx]
                ie, be = compute_coherence_raw(cand, inter)
                coherence = (ie / be) if be > 0 else (10.0 if ie > 0 else 0.0)

                updated_knot = TopologicalKnot(
                    id=knot.id,
                    vertices=set(cand),
                    age=knot.age + 10,
                    max_size=max(knot.max_size, len(cand)),
                    min_size=min(knot.min_size, len(cand)),
                    radius=component_radius(cand, inter),
                    coherence=coherence,
                    velocity=0.0,
                    velocity_avg=knot.velocity_avg,
                    mass=knot.mass,
                    momentum=knot.momentum,
                    position_history=list(knot.position_history),
                )

                mean_pos = sum(cand) / len(cand)
                prev_pos = (
                    knot.position_history[-1][1]
                    if knot.position_history
                    else mean_pos
                )
                updated_knot.velocity = abs(mean_pos - prev_pos) / 10.0

                updated_knot.position_history.append((self.time, mean_pos, coherence))
                if len(updated_knot.position_history) > 100:
                    updated_knot.position_history = updated_knot.position_history[-100:]

                next_active_knots[updated_knot.id] = updated_knot
            else:
                if knot.age >= 50:
                    self.dead_knots.append(knot)

        self.coupled_vertices.clear()
        active_ids = list(next_active_knots.keys())

        for kid in active_ids:
            knot = next_active_knots[kid]
            knot.mass = len(knot.vertices) * (knot.coherence ** 2)
            hist = knot.position_history
            if len(hist) > 1:
                t1, p1, _ = hist[0]
                t2, p2, _ = hist[-1]
                dt = t2 - t1
                if dt > 0:
                    knot.velocity_avg = ((p2 - p1) / dt, 0.0)
            knot.momentum = knot.mass * knot.velocity_avg[0]
            next_active_knots[kid] = knot

        current_overlaps = set()
        for i in range(len(active_ids)):
            for j in range(i + 1, len(active_ids)):
                id_a = active_ids[i]
                id_b = active_ids[j]
                knot_a = next_active_knots[id_a]
                knot_b = next_active_knots[id_b]

                intersection = len(knot_a.vertices.intersection(knot_b.vertices))
                if intersection > 0:
                    pair = (id_a, id_b) if id_a < id_b else (id_b, id_a)
                    current_overlaps.add(pair)

                    chi = intersection / max(min(len(knot_a.vertices), len(knot_b.vertices)), 1)
                    denom = max((knot_a.coherence ** 2 + knot_b.coherence ** 2), 1e-6)
                    res = (2.0 * knot_a.coherence * knot_b.coherence) / denom

                    if pair not in self.active_interactions:
                        pre_a_tuple = knot_pre_stats.get(id_a, (0.0, 0, 0.0))
                        pre_b_tuple = knot_pre_stats.get(id_b, (0.0, 0, 0.0))
                        m_a = pre_a_tuple[1] * (pre_a_tuple[0] ** 2)
                        m_b = pre_b_tuple[1] * (pre_b_tuple[0] ** 2)

                        self.active_interactions[pair] = InteractionEvent(
                            time=self.time,
                            knot_a=id_a,
                            knot_b=id_b,
                            overlap_size=intersection,
                            overlap_depth=chi,
                            resonance=res,
                            pre_a=(m_a, knot_a.velocity, m_a * knot_a.velocity, knot_a.velocity_avg),
                            pre_b=(m_b, knot_b.velocity, m_b * knot_b.velocity, knot_b.velocity_avg),
                            post_a=None,
                            post_b=None,
                        )

                    if chi > 0.4:
                        self.coupled_vertices.update(knot_a.vertices)
                        self.coupled_vertices.update(knot_b.vertices)

        finished = []
        for pair, ev in self.active_interactions.items():
            if pair not in current_overlaps:
                id_a, id_b = pair
                k_a = next_active_knots.get(id_a)
                k_b = next_active_knots.get(id_b)
                if k_a is not None:
                    ev.post_a = (k_a.mass, k_a.velocity, k_a.momentum, k_a.velocity_avg)
                if k_b is not None:
                    ev.post_b = (k_b.mass, k_b.velocity, k_b.momentum, k_b.velocity_avg)
                finished.append(pair)

        for pair in finished:
            ev = self.active_interactions.pop(pair)
            self.interaction_events.append(ev)

        for idx, cand in enumerate(candidates):
            if idx in matched_candidates:
                continue

            ie, be = compute_coherence_raw(cand, inter)
            coherence = (ie / be) if be > 0 else (10.0 if ie > 0 else 0.0)

            if coherence > 1.1 or len(cand) > 10:
                kid = self.time * 1000 + idx
                mean_pos = sum(cand) / len(cand)
                new_knot = TopologicalKnot(
                    id=kid,
                    vertices=set(cand),
                    age=10,
                    max_size=len(cand),
                    min_size=len(cand),
                    radius=component_radius(cand, inter),
                    coherence=coherence,
                    velocity=0.0,
                    velocity_avg=(0.0, 0.0),
                    mass=len(cand) * (coherence ** 2),
                    momentum=0.0,
                    position_history=[(self.time, mean_pos, coherence)],
                )
                next_active_knots[kid] = new_knot

        self.active_knots = next_active_knots

    def update_stability(self, _inter):
        stability_decay = 0.975
        stability_gain = 1.0

        for v in list(self.stability.keys()):
            self.stability[v] *= stability_decay

        for knot in self.active_knots.values():
            for v in knot.vertices:
                self.stability[v] = self.stability.get(v, 0.0) + stability_gain

        self.stability = {v: s for v, s in self.stability.items() if v in self.H.vertices}

        for v in self.stability:
            if self.stability[v] > 30.0:
                self.stability[v] = 30.0

    def propose_rewrite(self, inter):
        self.attempted_rewrites += 1

        vertices = list(self.H.vertices.keys())
        if not vertices:
            return None

        anchor_v = random.choice(vertices)
        anchor_obj = self.H.vertices.get(anchor_v)

        clustering = local_clustering(inter, anchor_v)
        degree = float(len(inter.get(anchor_v, set())))

        total_degree = sum(len(n) for n in inter.values())
        avg_degree = max((total_degree / len(inter)) if inter else 1.0, 1.0)

        local_density = clustering * (degree / avg_degree)

        internal_edges = 0
        boundary_edges = 0

        neighbors = inter.get(anchor_v)
        if neighbors is not None:
            neighborhood = set(neighbors)
            neighborhood.add(anchor_v)

            for n in neighborhood:
                for nn in inter.get(n, set()):
                    if nn in neighborhood:
                        internal_edges += 1
                    else:
                        boundary_edges += 1
            internal_edges //= 2

        if boundary_edges > 0:
            coherence = internal_edges / boundary_edges
        elif internal_edges > 0:
            coherence = 10.0
        else:
            coherence = 0.0

        alpha_base = 2.0
        lam = 0.5
        survival_threshold = 1.0
        neighborhood_size = len(inter.get(anchor_v, set())) + 1

        coherence_boost = (
            lam * (coherence - survival_threshold)
            if neighborhood_size >= 4 and coherence > survival_threshold
            else 0.0
        )

        mu = 0.3
        gamma = 2.2
        stability_cap = 30.0
        vertex_stability = self.stability.get(anchor_v, 0.0)
        normalized_stability = min(vertex_stability / stability_cap, 1.0)
        memory_contribution = mu * stability_cap * (normalized_stability ** gamma)

        alpha_eff = alpha_base + coherence_boost + memory_contribution

        coupling_modifier = 0.2 if anchor_v in self.coupled_vertices else 1.0
        rewrite_prob = math.exp(-(alpha_eff * coupling_modifier) * local_density)

        if random.random() > rewrite_prob:
            self.suppressed_rewrites += 1
            return None

        theta = 1.3
        beta = 1.5
        growth = beta if coherence > theta else 0.0

        boundary_ratio = (1.0 / coherence) if coherence > 0.0 else 10.0
        gamma_boundary = 20.0
        boundary_term = 1.0 / (1.0 + gamma_boundary * boundary_ratio)

        growth_bias = 1.0 + growth * boundary_term

        p_creation = min(0.90 * growth_bias, 0.99)
        p_fusion = min(0.05 / growth_bias, 0.99)

        if random.random() < p_creation:
            return edge_creation_rule(self.H, anchor_vertex=anchor_obj, p_rule=self.p_create)

        if len(self.H.vertices) > 200 and random.random() < p_fusion:
            return vertex_fusion_rule(self.H, anchor_vertex=anchor_obj)

        return None

    def propagate_xi(self, inter, clusters):
        new_xi = dict(self.xi)
        xi_max = 1e6

        protect_clusters = self.forced_time is not None and (self.time - self.forced_time) < 999999

        for v, xi_v in self.xi.items():
            if xi_v < self.xi_threshold:
                continue

            cid_v = clusters.get(v)
            xi_v_decayed = xi_v * self.XI_DECAY

            neighbors = inter.get(v, set())
            deg = max(float(len(neighbors)), 1.0)

            for u in neighbors:
                cid_u = clusters.get(u)

                if protect_clusters and cid_u is not None and cid_v is not None and cid_u != cid_v:
                    continue

                new_xi[u] = new_xi.get(u, 0.0) + 0.15 * xi_v_decayed / deg

            new_xi[v] = new_xi.get(v, 0.0) + 0.7 * xi_v_decayed

        for v in list(new_xi.keys()):
            if new_xi[v] > xi_max:
                new_xi[v] = xi_max

        self.xi = new_xi

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
                for w in inter.get(u, set()):
                    if w in xi_vertices and w not in visited:
                        visited.add(w)
                        clusters[w] = cid
                        stack.append(w)

            cid += 1

        return clusters

    def topo_clusters(self, inter):
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
                for w in inter.get(u, set()):
                    if w not in visited:
                        visited.add(w)
                        clusters[w] = cid
                        stack.append(w)

            cid += 1

        return clusters

    def update_topo_distance_memory(self, inter, restrict_to):
        topo = self.topo_clusters(inter)
        topo_groups = defaultdict(list)

        for v in restrict_to:
            cid = topo.get(v)
            if cid is not None:
                topo_groups[cid].append(v)

        topo_ids = list(topo_groups.keys())
        if not topo_ids:
            return

        max_depth = self.geometry_depth()

        if len(topo_ids) == 1:
            verts = topo_groups[topo_ids[0]]
            if len(verts) >= 2:
                mid = len(verts) // 2
                A = verts[:mid][:25]
                B = set(verts[mid:])
                d = min(self.graph_distance(inter, v, B, max_depth=max_depth) for v in A)

                if math.isfinite(d):
                    key = ("topo", topo_ids[0], topo_ids[0])
                    prev = self.topo_distance_memory.get(key, d)
                    self.topo_distance_memory[key] = (
                        self.DISTANCE_MEMORY_DECAY * prev
                        + (1 - self.DISTANCE_MEMORY_DECAY) * d
                    )

        for i in range(len(topo_ids)):
            for j in range(i + 1, len(topo_ids)):
                A = topo_groups[topo_ids[i]][:25]
                B = set(topo_groups[topo_ids[j]])

                d = min(self.graph_distance(inter, v, B, max_depth=max_depth) for v in A)
                if not math.isfinite(d):
                    continue

                key = ("topo", topo_ids[i], topo_ids[j])
                prev = self.topo_distance_memory.get(key, d)
                self.topo_distance_memory[key] = (
                    self.DISTANCE_MEMORY_DECAY * prev
                    + (1 - self.DISTANCE_MEMORY_DECAY) * d
                )

    def update_xi_distance_memory(self, inter):
        xi_clusters = self.xi_clusters(inter)

        cluster_to_vertices = defaultdict(list)
        for v, cid in xi_clusters.items():
            cluster_to_vertices[cid].append(v)

        cluster_ids = list(cluster_to_vertices.keys())
        if not cluster_ids:
            return

        max_depth = self.geometry_depth()

        if len(cluster_ids) == 1:
            verts = cluster_to_vertices[cluster_ids[0]]
            if len(verts) >= 2:
                mid = len(verts) // 2
                A = verts[:mid][:25]
                B = set(verts[mid:])
                d = min(self.graph_distance(inter, v, B, max_depth=max_depth) for v in A)

                if math.isfinite(d):
                    key = ("xi", cluster_ids[0], cluster_ids[0])
                    prev = self.xi_distance_memory.get(key, d)
                    self.xi_distance_memory[key] = (
                        self.DISTANCE_MEMORY_DECAY * prev
                        + (1 - self.DISTANCE_MEMORY_DECAY) * d
                    )
                    if self.verbose:
                        self._log(f"[geom-add] xi_pair (intra-cluster) ({cluster_ids[0]}, {cluster_ids[0]}) d={d}")

        for i in range(len(cluster_ids)):
            for j in range(i + 1, len(cluster_ids)):
                A = cluster_to_vertices[cluster_ids[i]][:25]
                B = set(cluster_to_vertices[cluster_ids[j]])

                d = min(self.graph_distance(inter, v, B, max_depth=max_depth) for v in A)

                if not math.isfinite(d):
                    continue

                key = ("xi", cluster_ids[i], cluster_ids[j])
                prev = self.xi_distance_memory.get(key, d)
                self.xi_distance_memory[key] = (
                    self.DISTANCE_MEMORY_DECAY * prev
                    + (1 - self.DISTANCE_MEMORY_DECAY) * d
                )

                if self.verbose:
                    self._log(f"[geom-add] xi_pair ({cluster_ids[i]}, {cluster_ids[j]}) d={d}")

    def record_xi_current(self, _inter):
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

    def touched_vertices(self):
        if self.last_rewrite is None:
            return set()

        touched = set(self.last_rewrite.get("added_vertices", []))
        removed_v = self.last_rewrite.get("removed_vertex")
        if removed_v is not None:
            touched.add(removed_v.id)

        return touched

    def geometry_depth(self):
        return max(16, int(math.log2(len(self.H.vertices) + 1) * 4))

    def graph_distance(self, inter, start, targets, max_depth):
        if start in targets:
            return 0

        visited = {start}
        frontier = {start}
        depth = 0

        while frontier and depth < max_depth:
            depth += 1
            nxt = set()
            for v in frontier:
                for u in inter.get(v, set()):
                    if u in visited:
                        continue
                    if u in targets:
                        return depth
                    visited.add(u)
                    nxt.add(u)
            frontier = nxt

        return float("inf")

    def undo_changes(self, undo):
        if "removed_vertex" in undo and undo["removed_vertex"] is not None:
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

    def force_defect(self, magnitude, max_tries=30):
        if not self.H.vertices:
            return False

        vertex_ids = list(self.H.vertices.keys())

        for _ in range(max_tries):
            vid = random.choice(vertex_ids)
            v_obj = self.H.vertices.get(vid)
            undo = edge_creation_rule(self.H, anchor_vertex=v_obj, p_rule=self.p_create)

            if undo is not None:
                self.xi[vid] = self.xi.get(vid, 0.0) + magnitude
                self.forced_time = self.time

                if self.verbose:
                    self._log(f"[inject] defect at t={self.time} v={vid}")

                self.last_rewrite = {
                    "added_vertices": list(undo.get("added_vertices", [])),
                    "removed_vertex": undo.get("removed_vertex"),
                    "kept_vertex": undo.get("kept_vertex"),
                    "added_edges": [],
                    "added_causal": [],
                    "removed_edges": {},
                    "old_causal": {},
                }
                return True

        return False

    def force_second_proto_object(self, omega_kick, xi_seed, min_distance, max_tries=50):
        _ = omega_kick

        xi_support = {
            vid for vid, x in self.xi.items()
            if x > self.xi_threshold and vid in self.H.vertices
        }

        if not xi_support:
            return False

        inter = worldline_interaction_graph(self.H, fraction=0.0)
        N = max(len(self.H.vertices), 1)
        max_depth = max(20, int(math.log2(N)) * 4)

        reachable = set(xi_support)
        frontier = set(xi_support)
        depth = 0

        while frontier and depth < max_depth:
            depth += 1
            nxt = set()
            for v in frontier:
                for u in inter.get(v, set()):
                    if u not in reachable:
                        reachable.add(u)
                        nxt.add(u)
            frontier = nxt

        candidates = list(reachable - xi_support)
        if not candidates:
            candidates = list(self.H.vertices.keys())

        best_vid = None
        best_d = -1

        for _ in range(max_tries):
            vid = random.choice(candidates)
            if vid in xi_support:
                continue

            d = self.graph_distance(inter, vid, xi_support, max_depth=max_depth)

            if d > best_d:
                best_d = d
                best_vid = vid

            if d >= min_distance and math.isfinite(d):
                self.xi[vid] = xi_seed
                self.forced_time = self.time
                if self.verbose:
                    self._log(f"### SECOND PROBE at t={self.time} | v={vid} | d={d}")
                return True

        if best_vid is not None:
            self.xi[best_vid] = xi_seed
            u = next(iter(xi_support))
            self.pending_bridge = (u, best_vid)
            self.pending_bridge_time = self.time
            self.forced_time = self.time
            if self.verbose:
                self._log(
                    f"### SECOND PROBE (fallback) at t={self.time} | "
                    f"v={best_vid} | d={best_d}"
                )
            return True

        return False

    def export_cluster_geometry(self):
        return {
            "topo": {
                f"{a},{b}": float(d)
                for (_, a, b), d in self.topo_distance_memory.items()
                if math.isfinite(d)
            },
            "xi": {
                f"{a},{b}": float(d)
                for (_, a, b), d in self.xi_distance_memory.items()
                if math.isfinite(d)
            },
        }
