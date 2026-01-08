# engine/rewrite_engine.py

import random
import math

from engine.observables import hierarchical_closure
from engine.rules import edge_creation_rule, vertex_fusion_rule
from engine.observables import (
    worldline_interaction_graph,
    interaction_concentration,
    closure_density
)
from engine.physics_params import (
    GAMMA_DEFECT,
    INERTIA_SCALE,
    INTERACTION_BOOST
)

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
    ):
        self.H = hypergraph
        self.p_create = p_create

        self.gamma_time = gamma_time
        self.gamma_ext = gamma_ext
        self.gamma_closure = gamma_closure
        self.gamma_hier = gamma_hier
        self.cluster_omega_memory = {}
        # Ω-locking memory (proto-particle seed)
        self.trapped_omega = 0.0
        self._prev_trapped_omega = 0.0
        self.cluster_omega = {}

        self.epsilon_label_violation = epsilon_label_violation

        # influence field
        self.xi = {}
        self.XI_DECAY = XI_DECAY
        self.XI_COUPLING = XI_COUPLING

        self.defect_log = []
        self.rewrite_history = []
        self.last_rewrite = None

        self.forced_time = None
        self.time = 0

        if seed is not None:
            random.seed(seed)

    # --------------------------------------------------
    # Main step
    # --------------------------------------------------
    def step(self):

        # --------------------------------------------------
        # Measure BEFORE
        # --------------------------------------------------
        L_before = self.H.max_chain_length()
        inter_before = worldline_interaction_graph(self.H)
        phi_before = interaction_concentration(inter_before)
        psi_before = closure_density(inter_before)
        omega_before = hierarchical_closure(self.H, inter_before)

        # --------------------------------------------------
        # Rewrite proposal (STRONGLY ξ-biased)
        # --------------------------------------------------
        protected = {
            v for v, xi_v in self.xi.items()
            if xi_v > 1e-6 and v in self.H.vertices
        }

        undo = None
        if protected:
            if random.random() < 0.7:
                v = random.choice(list(protected))
                undo = edge_creation_rule(self.H, anchor_vertex=v)
            else:
                if random.random() < self.p_create:
                    undo = edge_creation_rule(self.H)
                else:
                    undo = vertex_fusion_rule(self.H)
        else:
            if random.random() < self.p_create:
                undo = edge_creation_rule(self.H)
            else:
                undo = vertex_fusion_rule(self.H)

        if undo is None:
            self.time += 1
            return False
        #UTILITY ---
        
        # --------------------------------------------------
        # Track touched vertices
        # --------------------------------------------------
        self.last_rewrite = {
            "added_vertices": undo.get("added_vertices", []),
            "removed_vertices": (
                [undo["removed_vertex"].id]
                if "removed_vertex" in undo else []
            ),
            "added_edges": undo.get("added_edges", []),
        }

        # --------------------------------------------------
        # Measure AFTER
        # --------------------------------------------------
        L_after = self.H.max_chain_length()
        delta_L = L_after - L_before

        inter_after = worldline_interaction_graph(self.H)
        phi_after = interaction_concentration(inter_after)
        psi_after = closure_density(inter_after)
        omega_after = hierarchical_closure(self.H, inter_after)

        delta_phi = phi_after - phi_before
        delta_psi = psi_after - psi_before
        delta_omega = omega_after - omega_before

        # --------------------------------------------------
        # ξ CLUSTER IDENTIFICATION
        # --------------------------------------------------
        clusters_before = self.xi_clusters(inter_before)
        clusters_after  = self.xi_clusters(inter_after)

        # --------------------------------------------------
        # PER-CLUSTER Ω MEMORY
        # --------------------------------------------------
        cluster_omega_now = {}
        for v, cid in clusters_after.items():
            cluster_omega_now.setdefault(cid, []).append(
                local_omega(self.H, inter_after, v)
            )

        CLUSTER_OMEGA_DECAY = 0.9
        for cid, vals in cluster_omega_now.items():
            mean_omega = sum(vals) / len(vals)
            prev = self.cluster_omega.get(cid, mean_omega)
            self.cluster_omega[cid] = (
                CLUSTER_OMEGA_DECAY * prev
                + (1.0 - CLUSTER_OMEGA_DECAY) * mean_omega
            )

        # --------------------------------------------------
        # Ω-GRADIENT (local)
        # --------------------------------------------------
        touched = self.touched_vertices()
        local_vals = [
            local_omega(self.H, inter_after, v)
            for v in touched if v in self.H.vertices
        ]
        grad_omega = (
            max(local_vals) - min(local_vals)
            if len(local_vals) >= 2 else 0.0
        )

        # --------------------------------------------------
        # Ω-GRADIENT MEMORY
        # --------------------------------------------------
        if not hasattr(self, "omega_memory"):
            self.omega_memory = 0.0

        OMEGA_MEMORY_DECAY = 0.85
        self.omega_memory = (
            OMEGA_MEMORY_DECAY * self.omega_memory
            + (1.0 - OMEGA_MEMORY_DECAY) * grad_omega
        )

        grad_omega_eff = grad_omega + 0.5 * self.omega_memory

        # --------------------------------------------------
        # DEFECT LOGGING
        # --------------------------------------------------
        if abs(delta_omega) > self.epsilon_label_violation:
            self.defect_log.append({
                "time": self.time,
                "birth_time": self.time,
                "delta_Q": delta_omega,
                "V": len(self.H.vertices),
                "L": L_after,
                "omega": omega_after
            })

        # --------------------------------------------------
        # ACCEPTANCE PROBABILITY
        # --------------------------------------------------
        accept_prob = 1.0
        
        # --------------------------------------------------
        # ξ CLUSTER FRAGMENTATION PENALTY
        # --------------------------------------------------
        fragmentation_penalty = 0.0

        # clusters_before and clusters_after already computed above
        for cid in set(clusters_before.values()):
            before_size = sum(
                1 for v in clusters_before if clusters_before[v] == cid
            )
            after_size = sum(
                1 for v in clusters_after if clusters_after[v] == cid
            )

            # Penalize loss of cluster members
            if after_size < before_size:
                fragmentation_penalty += (before_size - after_size)

        CLUSTER_COHESION = 2.5   # strong on purpose
        accept_prob *= math.exp(-CLUSTER_COHESION * fragmentation_penalty)
        
        # --------------------------------------------------
        # ξ–ξ LOCAL BINDING REWARD (PRE-PARTICLE GLUE)
        # --------------------------------------------------
        binding_reward = 0.0

        touched = self.touched_vertices()
        for v in touched:
            if self.xi.get(v, 0.0) < 1e-6 or v not in self.H.vertices:
                continue
            
            neighbors = inter_after.get(v, [])
            for u in neighbors:
                if self.xi.get(u, 0.0) > 1e-6:
                    binding_reward += 1.0

        # Each ξ–ξ adjacency counted twice → normalize
        binding_reward *= 0.5

        XI_BINDING_STRENGTH = 0.15   # start small
        accept_prob *= math.exp(XI_BINDING_STRENGTH * binding_reward)
        
        # prevent numerical blow-up
        binding_term = XI_BINDING_STRENGTH * binding_reward
        binding_term = max(min(binding_term, 5.0), -5.0)

        accept_prob *= math.exp(binding_term)
        if binding_reward > 0 and self.time % 50 == 0:
            print(f"[bind] t={self.time} reward={binding_reward:.2f}")
        # --------------------------------------------------
        # 🔥 CLUSTER Ω STABILITY PENALTY (THIS IS THE KEY)
        # --------------------------------------------------
        cluster_penalty = 0.0

        for v, cid in clusters_after.items():
            if cid not in self.cluster_omega:
                continue

            omega_now = self.cluster_omega[cid]
            omega_prev = self.cluster_omega.get(cid, omega_now)

            if omega_now < omega_prev:
                cluster_penalty += (omega_prev - omega_now)

        CLUSTER_BINDING = 1.2
        accept_prob *= math.exp(-CLUSTER_BINDING * cluster_penalty)

        # --------------------------------------------------
        # Standard stability terms
        # --------------------------------------------------
        if self.forced_time is None or (self.time - self.forced_time) > 20:
            accept_prob *= math.exp(-0.15 * grad_omega_eff)

        if delta_L < 0:
            accept_prob *= math.exp(self.gamma_time * delta_L)

        if delta_phi > 0:
            accept_prob *= math.exp(-self.gamma_ext * delta_phi)

        if delta_psi > 0:
            accept_prob *= math.exp(self.gamma_closure * delta_psi)

        if delta_omega > 0:
            accept_prob *= math.exp(self.gamma_hier * delta_omega)

        if abs(delta_omega) > self.epsilon_label_violation:
            V = len(self.H.vertices)
            gamma_defect = GAMMA_DEFECT * math.exp(-V / 800)
            accept_prob *= math.exp(-gamma_defect * abs(delta_omega))

        # --------------------------------------------------
        # ACCEPT / REJECT
        # --------------------------------------------------
        accepted = random.random() <= accept_prob

        if not accepted:
            self.undo_changes(undo)
        else:
            # ξ inheritance
            parents = [
                v for v in self.touched_vertices()
                if v in self.xi and self.xi[v] > 1e-6
            ]

            for vid in self.last_rewrite["added_vertices"]:
                if parents:
                    inherited = sum(self.xi[p] for p in parents) / len(parents)
                    self.xi[vid] = self.xi.get(vid, 0.0) + 0.5 * inherited

            self._propagate_xi(inter_after)
            # --------------------------------------------------
            # Record rewrite WITH cluster information
            # --------------------------------------------------
            clusters_after = self.xi_clusters(inter_after)

            rewrite_entry = {
                "time": self.time,
                "rewrite": undo,
                "xi_support": [
                    v for v in clusters_after.keys()
                    if v in self.touched_vertices()
                ],
                "cluster_ids": list({
                    clusters_after[v]
                    for v in clusters_after
                    if v in self.touched_vertices()
                }),
                "cluster_sizes": {
                    cid: sum(1 for v in clusters_after if clusters_after[v] == cid)
                    for cid in set(clusters_after.values())
                },
                "cluster_omega": dict(self.cluster_omega),
            }

            self.rewrite_history.append(rewrite_entry)

        self.time += 1
        return accepted

    # --------------------------------------------------
    # ξ CLUSTER IDENTIFICATION
    # --------------------------------------------------
    def xi_clusters(self, inter):
        """
        Identify connected components of ξ-support
        in the interaction graph.

        Returns:
            dict: vertex_id -> cluster_id
        """
        clusters = {}
        visited = set()
        cid = 0

        xi_vertices = {
            v for v, x in self.xi.items()
            if x > 1e-6 and v in self.H.vertices
        }

        for v in xi_vertices:
            if v in visited:
                continue

            stack = [v]
            visited.add(v)
            clusters[v] = cid

            while stack:
                u = stack.pop()
                for nbr in inter.get(u, []):
                    if nbr in xi_vertices and nbr not in visited:
                        visited.add(nbr)
                        clusters[nbr] = cid
                        stack.append(nbr)

            cid += 1

        return clusters
    # --------------------------------------------------
    # Forced probe (Path A)
    # --------------------------------------------------
    def force_defect(self, magnitude=0.3):

        v = random.choice(list(self.H.vertices.keys()))
        undo = edge_creation_rule(self.H, anchor_vertex=v)

        if undo is None:
            return False

        # seed xi on anchor and causal future
        self.xi[v] = self.xi.get(v, 0.0) + magnitude
        for u in undo.get("added_vertices", []):
            self.xi[u] = self.xi.get(u, 0.0) + 0.5 * magnitude

        self.last_rewrite = {
            "added_vertices": undo.get("added_vertices", []),
            "removed_vertices": [],
            "added_edges": undo.get("added_edges", []),
        }

        inter = worldline_interaction_graph(self.H)
        omega = hierarchical_closure(self.H, inter)

        self.defect_log.append({
            "time": self.time,
            "birth_time": self.time,
            "delta_Q": magnitude,
            "omega": omega,
            "forced": True,
            "anchor_vertex": v
        })

        self.forced_time = self.time
        self.record_rewrite(undo)
        self.time += 1
        return True

    # --------------------------------------------------
    # ξ propagation (single, clean)
    # --------------------------------------------------
    def _propagate_xi(self, inter):
        new_xi = dict(self.xi)

        for v, xi_v in self.xi.items():
            if xi_v < 1e-6:
                continue

            xi_v *= self.XI_DECAY
            neighbors = inter.get(v, [])

            if neighbors:
                share = xi_v / len(neighbors)
                for u in neighbors:
                    new_xi[u] = new_xi.get(u, 0.0) + 0.5 * share

            new_xi[v] = new_xi.get(v, 0.0) + 0.5 * xi_v

        self.xi = new_xi

    # --------------------------------------------------
    # Utilities
    # --------------------------------------------------
    def touched_vertices(self):
        if self.last_rewrite is None:
            return set()
        return set(
            self.last_rewrite.get("added_vertices", []) +
            self.last_rewrite.get("removed_vertices", [])
        )

    def record_rewrite(self, undo):
        if not hasattr(self, "rewrite_history"):
            self.rewrite_history = []

        # --- determine vertices touched by this rewrite ---
        touched = set(undo.get("added_vertices", []))

        if "removed_vertex" in undo:
            touched.add(undo["removed_vertex"].id)

        self.rewrite_history.append({
            "time": self.time,
            "rewrite": {
                "added_vertices": undo.get("added_vertices", []),
                "removed_vertices": (
                    [undo["removed_vertex"].id]
                    if "removed_vertex" in undo else []
                ),
                "added_edges": undo.get("added_edges", []),
                "removed_edges": list(undo.get("removed_edges", {}).keys()),
            },
            "grad_omega": getattr(self, "_last_grad_omega", None),

            # ✅ THIS IS THE FIX
            "xi_support": [
                v for v in touched
                if self.xi.get(v, 0.0) > 1e-6
            ],
        })
        #---Temp debug print---
########print(f"[DEBUG] t={self.time} xi_support={self.rewrite_history[-1]['xi_support']}")
        #----------------------  
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