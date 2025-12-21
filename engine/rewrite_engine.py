# engine/rewrite_engine.py

import random
import math
import copy

from engine.observables import hierarchical_closure
from engine.rules import edge_creation_rule, vertex_fusion_rule
from engine.observables import adjacency_overlap
from engine.observables import (
    worldline_interaction_graph,
    interaction_concentration,
    closure_density
)


class RewriteEngine:
    """
    Time + space emergence via inertia biases.
    """

    def __init__(
        self,
        hypergraph,
        p_create=0.6,
        seed=None,
        gamma_time=0.1,
        gamma_space=0.1,
        gamma_ext=0.05,
        defect_log = [],
        gamma_closure=0.05,
        epsilon_label_violation = 0.05,
        gamma_hier=0.06
    ):
        self.H = hypergraph
        self.p_create = p_create
        self.gamma_time = gamma_time
        self.gamma_space = gamma_space
        self.gamma_ext = gamma_ext
        self.gamma_closure = gamma_closure
        self.gamma_hier = gamma_hier
        self.defect_log = defect_log
        self.epsilon_label_violation = epsilon_label_violation
        self.time = 0

        if seed is not None:
            random.seed(seed)

    def step(self):
        
        # --- 1. Measure BEFORE ---
        L_before = self.H.max_chain_length()
        
        inter_before = worldline_interaction_graph(self.H)
        phi_before = interaction_concentration(inter_before)
        
        psi_before = closure_density(inter_before)
        
        omega_before = hierarchical_closure(self.H, inter_before)

        k_before = self.H.average_coordination()
        
        
        # --- 2. Propose rewrite ---
        if random.random() < self.p_create:
            undo = edge_creation_rule(self.H)
        else:
            undo = vertex_fusion_rule(self.H)

        if undo is None:
            self.time += 1
            return False

        # --- 3. Measure AFTER ---
        L_after = self.H.max_chain_length()
        delta_L = L_after - L_before

        inter_after = worldline_interaction_graph(self.H)
        phi_after = interaction_concentration(inter_after)
        delta_phi = phi_after - phi_before

        psi_after = closure_density(inter_after)
        delta_psi = psi_after - psi_before

        omega_after = hierarchical_closure(self.H, inter_after)
        delta_omega = omega_after - omega_before

        k_after = self.H.average_coordination()
        
        # --- Topological defect proxy (TEMPORARY) ---
        delta_Q = delta_omega

        if abs(delta_Q) > self.epsilon_label_violation:
            event = {
                "time": self.time,
                "delta_Q": delta_Q,
                "V": len(self.H.vertices),
                "k": k_after,
                "L": L_after,
                "omega": omega_after
            }
            self.defect_log.append(event)

            print(
                f"*** DEFECT EVENT at t={self.time} | "
                f"ΔQ={delta_Q:+.4e} | "
                f"V={event['V']} | "
                f"k={event['k']:.2f} ***"
            )
        
        # --- 4. Acceptance probability ---
        accept_prob = 1.0

        # Time inertia
        if delta_L < 0:
            accept_prob *= math.exp(self.gamma_time * delta_L)

        # Extensivity (hub suppression)
        if delta_phi > 0:
            accept_prob *= math.exp(-self.gamma_ext * delta_phi)

        # Closure (redundancy reward)
        if delta_psi > 0:
            accept_prob *= math.exp(self.gamma_closure * delta_psi)

        # Hierarchical stability
        if delta_omega > 0:
            accept_prob *= math.exp(self.gamma_hier * delta_omega)

        # --- 5. Geometricity constraint (THIS is what you add) ---
        V = len(self.H.vertices)
        k_target = 8.0
        lambda_k = 0.25 * (1 - math.exp(-V / 200))
        accept_prob *= math.exp(-lambda_k * (k_after - k_target)**2)
        
        # --- 5b. Topological defect suppression (soft conservation) ---
        gamma_defect = 0.15  # start small
        
        if abs(delta_Q) > self.epsilon_label_violation:
            
            accept_prob *= math.exp(-gamma_defect * abs(delta_Q))

        # --- 6. Accept or reject ---
        if random.random() > accept_prob:
            self.undo_changes(undo)  # undo rewrite
            self.time += 1
            return False

        self.time += 1
        return True
            
    def undo_changes(self, undo):
        
        # restore removed vertex
        if "removed_vertex" in undo:
        
            v = undo["removed_vertex"]
            self.H.vertices[v.id] = v
            self.H.causal_order[v.id] = set()

        # restore removed edges
        for eid, e in undo.get("removed_edges", {}).items():
            self.H.hyperedges[eid] = e

        # remove added edges
        for eid in undo.get("added_edges", []):
            self.H.hyperedges.pop(eid, None)

        # remove added vertices
        for vid in undo.get("added_vertices", []):
            self.H.vertices.pop(vid, None)
            self.H.causal_order.pop(vid, None)

        # restore causal relations
        for u, past in undo.get("old_causal", {}).items():
            self.H.causal_order[u] = past
            
    def run(self, steps):
        for _ in range(steps):
            self.step()
            