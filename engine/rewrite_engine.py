# engine/rewrite_engine.py

from itertools import count
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
from engine.physics_params import (
    GAMMA_DEFECT,
    INERTIA_SCALE,
    INTERACTION_BOOST
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
        defect_log = None,
        gamma_closure=0.05,
        epsilon_label_violation = 0.08,
        gamma_hier=0.06
    ):
        self.H = hypergraph
        self.p_create = p_create
        self.gamma_time = gamma_time
        self.rewrite_history = []
        self.last_rewrite = None
        self.gamma_space = gamma_space
        self.particle_activity = {}
        self.gamma_ext = gamma_ext
        self.gamma_closure = gamma_closure
        self.gamma_hier = gamma_hier
        self.defect_log = defect_log if defect_log is not None else []
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
        
        # --- Dynamics --
        self.last_rewrite = {
            "added_vertices": undo.get("added_vertices", []),
            "removed_vertices": (
                [undo["removed_vertex"].id]
                if "removed_vertex" in undo else []
            ),
            "added_edges": undo.get("added_edges", []),
        }

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
                "birth_time": self.time,
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
                f"birth_time={event['birth_time']} | "
                f"k={event['k']:.2f} ***"
            )
            
        
        # --- 4. Acceptance probability ---
        accept_prob = 1.0
        k_target = 8.0
        
        if k_after > k_target + 0.8:
            accept_prob *= math.exp(-0.5 * (k_after - k_target)**2)  # discourage high connectivity
            

        

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
        if V < 300:
            lambda_k = 0.2 * (1 - math.exp(-V / 200))
        else:
            lambda_k = 0.6
            
        accept_prob *= math.exp(-lambda_k * (k_after - k_target)**2)
        
        # --- 5b. Topological defect suppression (soft conservation) ---
        gamma_defect = GAMMA_DEFECT * math.exp(-V / 800)  # start small
        
        if abs(delta_Q) > self.epsilon_label_violation:
            
            accept_prob *= math.exp(-gamma_defect * abs(delta_Q))
            
        # --- B1. Defect inertia (age-based stability) ---
        if abs(delta_Q) > self.epsilon_label_violation and self.defect_log:
            last_defect = self.defect_log[-1]
            age = self.time - last_defect.get("birth_time", self.time)
            inertia = math.exp(-INERTIA_SCALE / (age + 1.0))
            accept_prob *= inertia
            
        # --- Step B2: particle interaction bias ---
        interaction_boost = 1.0

        touched = self.touched_vertices()

        for pid, count in self.particle_activity.items():
        # recent activity → likely nearby particle
            if count > 0 and pid in touched:
                interaction_boost *= INTERACTION_BOOST # very weak

        accept_prob *= interaction_boost
        
        # --- Step C: particle survival bias ---
        if V < 300:
            survival_boost = 1.0
            touched = self.touched_vertices()

            for pid, count in self.particle_activity.items():
                if pid in touched and count > 3:
                    # protect against large topolog changes
                    if abs(delta_Q) > 0.15:
                        survival_boost *= 1.05  # mild penalty

            accept_prob *= survival_boost
            
        # --- Step 16: phase-locking (temporal coherence) ---
        if self.defect_log:
            last = self.defect_log[-1]
            dt = self.time - last["time"]

            # only reward near-aligned defects
            if 1 <= dt <= 8 and abs(delta_Q) < 0.25:
                phase_lock = math.exp(-(dt - 1) / 4.0)
                accept_prob *= (1.0 + 0.15 * phase_lock)
    
        # --- Step B3: mass consistency bias ---
        mass_penalty = 1.0

        for pid, activity in self.particle_activity.items():
            # activity ~ proxy for inverse mass
            mass_penalty *= math.exp(-0.01 * activity)

        accept_prob *= mass_penalty
        
        
        # --- 6. Accept or reject ---
        accepted = random.random() <= accept_prob

        if not accepted:
            self.undo_changes(undo)
        else:
            self.record_rewrite(undo)

        self.time += 1
        return accepted
    
        
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
            
    def record_rewrite(self, undo):
        if not hasattr(self, "rewrite_history"):
            self.rewrite_history = []

        self.rewrite_history.append({
            "time": self.time,
            "rewrite": {
                "added_vertices": undo.get("added_vertices", []),
                "removed_vertices": list(undo.get("removed_vertex", {}).keys())
                    if "removed_vertex" in undo else [],
                "added_edges": undo.get("added_edges", []),
                "removed_edges": list(undo.get("removed_edges", {}).keys())
            }
    })
        
    def touched_vertices(self):
        if self.last_rewrite is None:
            return set()
        return set(
            self.last_rewrite.get("added_vertices", [])
            + self.last_rewrite.get("removed_vertices", [])
        )
            
    def run(self, steps):
        for _ in range(steps):
            self.step()
            
def defect_support_vertices(engine):
    if not engine.defect_log:
        return set()
    return set(
        engine.last_rewrite.get("added_vertices", [])
        + engine.last_rewrite.get("removed_vertices", [])
    )            

