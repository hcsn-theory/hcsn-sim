# engine/rewrite_engine.py

import random
import math
from tracemalloc import start

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
        self.cluster_prev = {}
        # --- Cluster adjacency memory (proto-particle glue) ---
        self.cluster_links = {}        # frozenset({v,u}) -> strength
        self.CLUSTER_LINK_DECAY = 0.92
        self.CLUSTER_LINK_MAX   = 5.0
        self.CLUSTER_BINDING_STRENGTH = 0.25

        self.epsilon_label_violation = epsilon_label_violation

        # influence field
        self.xi = {}
        self.XI_DECAY = XI_DECAY
        self.XI_COUPLING = XI_COUPLING
        self.xi_centroid = None
        self.xi_threshold = 1e-6
        self.xi_surface_lambda = 0.03

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
        # ξ–ξ CLUSTER ADJACENCY MEMORY (spatial cohesion)
        # --------------------------------------------------
        new_links = {}

        for v, xi_v in self.xi.items():
            if xi_v < 1e-6 or v not in self.H.vertices:
                continue
            
            for u in inter_after.get(v, []):
                if self.xi.get(u, 0.0) > 1e-6:
                    key = frozenset((v, u))
                    prev = self.cluster_links.get(key, 0.0)
                    strength = min(prev + 1.0, self.CLUSTER_LINK_MAX)
                    new_links[key] = strength

        # decay old links
        for key, val in self.cluster_links.items():
            if key not in new_links:
                decayed = self.CLUSTER_LINK_DECAY * val
                if decayed > 1e-3:
                    new_links[key] = decayed

        self.cluster_links = new_links

        # --------------------------------------------------
        # ξ CLUSTER IDENTIFICATION
        # --------------------------------------------------
        clusters_before = self.xi_clusters(inter_before)
        clusters_after  = self.xi_clusters(inter_after)
        clusters_now    = clusters_after
        
        
        # --------------------------------------------------
        # ξ TRUE NUCLEATION REPULSION (new cluster protection)
        # --------------------------------------------------
        NUCLEATION_REPULSION = 3.0   # strong, but local
        
        new_cluster_ids = (
            set(clusters_after.values())
            - set(clusters_before.values())
        )
        
        if new_cluster_ids:
            for v, cid_v in clusters_after.items():
                if cid_v not in new_cluster_ids:
                    continue
                if self.xi.get(v, 0.0) < 1e-6:
                    continue
                
                for u in inter_after.get(v, []):
                    cid_u = clusters_after.get(u)
                    if cid_u is None:
                        continue
                    
                    if cid_u not in new_cluster_ids:
                        accept_prob *= math.exp(-NUCLEATION_REPULSION)
                        
            if self.time % 50 == 0:
                print(
                    f"[nucleate] t={self.time} "
                    f"new_clusters={len(new_cluster_ids)}"
                )

        # --------------------------------------------------
        # PER-CLUSTER Ω MEMORY
        # --------------------------------------------------
        prev_cluster_omega = dict(self.cluster_omega)
        cluster_omega_now = {}
        for v, cid in clusters_now.items():
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
        # ξ SPATIAL LOCALIZATION (diffusion suppression)
        # --------------------------------------------------
        xi_support = [v for v, x in self.xi.items() if x > 1e-6]
        
        if xi_support:
            new_centroid = sum(xi_support) / len(xi_support)

            if self.xi_centroid is None:
                xi_drift_penalty = 0.0
            else:
                xi_drift_penalty = abs(new_centroid - self.xi_centroid)

            self.xi_centroid = new_centroid
        else:
            xi_drift_penalty = 0.0
            self.xi_centroid = None
        
        
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
        # LOCAL Ω CONFINEMENT (proto-particle mass core)
        # --------------------------------------------------
        omega_cluster_before = []
        omega_cluster_after  = []
        omega_out_before     = []
        omega_out_after      = []
        
        xi_support_before = {
            v for v, x in self.xi.items()
            if x > 1e-6 and v in self.H.vertices
        }
        
        # ξ core + immediate boundary only
        boundary = set()
        for v in xi_support_before:
            boundary.update(inter_before.get(v, []))

        relevant = set(xi_support_before) | boundary

        for v in relevant:
            if v not in self.H.vertices:
                continue
            
            w_before = self.omega_potential(inter_before, v)
            w_after  = self.omega_potential(inter_after, v)

            if v in xi_support_before:
                omega_cluster_before.append(w_before)
                omega_cluster_after.append(w_after)
            else:
                omega_out_before.append(w_before)
                omega_out_after.append(w_after)
        
        # Safe means
        def mean(xs):
            return sum(xs) / len(xs) if xs else 0.0
        
        Ωc_before = mean(omega_cluster_before)
        Ωc_after  = mean(omega_cluster_after)
        Ωo_before = mean(omega_out_before)
        Ωo_after  = mean(omega_out_after)
        
        # Confinement signal
        delta_confined = (Ωc_after - Ωc_before) - (Ωo_after - Ωo_before)
        
        # --- omega trapping (mass memory) ---
        if delta_confined > 0:
            self.trapped_omega = (
                0.95 * self.trapped_omega
                + 0.05 * delta_confined
            )
        else:
            self.trapped_omega *= 0.95
        
        # --------------------------------------------------
        # CONFINEMENT PENALTY (mass emergence)
        # --------------------------------------------------
        OMEGA_CONFINEMENT_STRENGTH = 2.0  # start moderate
        
        if delta_confined < 0:
            # clamp to avoid overflow
            delta_confined = max(delta_confined, -5.0)
            accept_prob *= math.exp(
                OMEGA_CONFINEMENT_STRENGTH * delta_confined
            )
        
        # DEBUG
        if self.time % 100 == 0 and xi_support_before:
            print(
                f"[confine] t={self.time} "
                f"ΔΩ_conf={delta_confined:.3f} "
                f"Ωc={Ωc_after:.3f} Ωo={Ωo_after:.3f}"
            )
        
        # --------------------------------------------------
        # CLUSTER SIZE MASS TERM (prevents ξ condensation)
        # --------------------------------------------------
        cluster_size_penalty = 0.0
        
        for cid in set(clusters_after.values()):
            size = sum(1 for v in clusters_after if clusters_after[v] == cid)
        
            # quadratic cost favors finite size
            if size > 1:
                cluster_size_penalty += (size - 1) ** 2
        
        CLUSTER_MASS = 0.002   # START SMALL
        
        cluster_size_penalty = min(cluster_size_penalty, 100.0)
        
        accept_prob *= math.exp(-CLUSTER_MASS * cluster_size_penalty)
        
        if self.time % 200 == 0 and cluster_size_penalty > 0:
            print(
                f"[mass] t={self.time} "
                f"penalty={cluster_size_penalty:.1f}"
            )
        
        # --------------------------------------------------
        # ξ DIFFUSION PENALTY (localization mass)
        # --------------------------------------------------
        XI_DIFFUSION_STRENGTH = 0.02  # start very small

        xi_drift_penalty = min(xi_drift_penalty, 50)

        accept_prob *= math.exp(-XI_DIFFUSION_STRENGTH * xi_drift_penalty)

        if xi_drift_penalty > 0 and self.time % 100 == 0:
            print(
                f"[loc] t={self.time} "
                f"drift={xi_drift_penalty}"
            )

        # --------------------------------------------------
        # CLUSTER ADJACENCY STABILITY REWARD
        # --------------------------------------------------
        link_reward = sum(self.cluster_links.values())
        
        # hard clamp for numerical safety
        link_reward = min(link_reward, 10.0)
        
        CLUSTER_ADJ_REWARD = 0.05
        accept_prob *= math.exp(CLUSTER_ADJ_REWARD * link_reward)
        
        # debug
        if link_reward > 0 and self.time % 100 == 0:
            print(
                f"[adj] t={self.time} "
                f"links={len(self.cluster_links)} "
                f"reward={link_reward:.2f}"
            )
            
        # --------------------------------------------------
        # ξ SURFACE TENSION (forces compact clusters)
        # --------------------------------------------------
        surface_penalty = 0.0
        
        for v, xi_v in self.xi.items():
            if xi_v < 1e-6 or v not in self.H.vertices:
                continue
            
            neighbors = inter_after.get(v, [])
            xi_neighbors = sum(
                1 for u in neighbors
                if self.xi.get(u, 0.0) > 1e-6
            )
        
            # penalize exposed ξ (few neighbors)
            if xi_neighbors < 2:
                surface_penalty += (2 - xi_neighbors)
        
        SURFACE_TENSION = 0.8   # strong on purpose
        surface_penalty = min(surface_penalty, 50.0)
        
        accept_prob *= math.exp(-SURFACE_TENSION * surface_penalty)
        
        if self.time % 200 == 0 and surface_penalty > 0:
            print(
                f"[surface] t={self.time} "
                f"penalty={surface_penalty:.1f}"
            )

        
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

        CLUSTER_COHESION = 1.2   # strong on purpose
        accept_prob *= math.exp(-CLUSTER_COHESION * fragmentation_penalty)
        
        # --------------------------------------------------
        # ξ–ξ LOCAL BINDING REWARD (PRE-PARTICLE GLUE)
        # --------------------------------------------------
        binding_reward = 0.0

        touched = self.touched_vertices()
        for v in touched:
            if self.xi.get(v, 0.0) < 1e-6 or v not in self.H.vertices:
                continue
            
            for u in inter_after.get(v, []):
                if self.xi.get(u, 0.0) > 1e-6:
                    binding_reward += 1.0

        # normalize double counting
        binding_reward *= 0.5

        XI_BINDING_STRENGTH = 0.15
        binding_term = XI_BINDING_STRENGTH * binding_reward

        # hard clamp (critical)
        binding_term = max(min(binding_term, 5.0), 0.0)

        accept_prob *= math.exp(binding_term)

        # debug
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
            omega_prev = prev_cluster_omega.get(cid, omega_now)

            if omega_now < omega_prev:
                cluster_penalty += (omega_prev - omega_now)

        CLUSTER_BINDING = 1.2
        accept_prob *= math.exp(-CLUSTER_BINDING * cluster_penalty)
        # --- DEBUG: cluster Ω stability ---
        if cluster_penalty > 0 and self.time % 50 == 0:
            print(
                f"[cluster] t={self.time} "
                f"penalty={cluster_penalty:.3f} "
                f"clusters={len(self.cluster_omega)}"
            )
            
        # --------------------------------------------------
        # CLUSTER COHESION PENALTY (proto-particle mass)
        # --------------------------------------------------
        binding_loss = 0.0

        touched = self.touched_vertices()
        for key, strength in self.cluster_links.items():
            v, u = tuple(key)

            # penalize if rewrite breaks a strong ξ–ξ link
            if (v in touched or u in touched):
                if u not in inter_after.get(v, []):
                    binding_loss += strength

        # clamp to prevent overflow
        binding_loss = min(binding_loss, 10.0)

        accept_prob *= math.exp(
            -self.CLUSTER_BINDING_STRENGTH * binding_loss
        )
                
        
        
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
        
        # --- DEBUG: proto-particle candidate ---
        if self.time % 100 == 0:
           xi_support = [v for v, x in self.xi.items() if x > 1e-6]
           if len(xi_support) >= 2:
               print(
                   f"[proto?] t={self.time} "
                   f"|ξ|={len(xi_support)} "
                   f"Ω_trapped={getattr(self, 'trapped_omega', 0.0):.3f}"
               )
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
                    
            
            clusters_now = self.xi_clusters(inter_after)
            self._propagate_xi(inter_after, clusters_now)
            # --- ξ surface tension (localization) ---
            xi_support = {
                v for v, x in self.xi.items()
                if x > self.xi_threshold
            }
            
            if xi_support:
                boundary = self.xi_boundary(xi_support, inter_after)
                
                for v in boundary:
                    self.xi[v] -= self.xi_surface_lambda
                    if self.xi[v] < 0.0:
                        self.xi[v] = 0.0
            # --------------------------------------------------
            # Record rewrite WITH cluster information
            # -------------------------------------------   -------
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
    # ξ BOUNDARY IDENTIFICATION
    # --------------------------------------------------
    def xi_boundary(self, xi_support, inter):
        """
        Compute ξ-boundary vertices using hyperedge incidence.
        A vertex is boundary if it shares a hyperedge with a non-ξ vertex.
        """
        boundary = set()

        for v in xi_support:
            for u in inter.get(v, []):
                if u not in xi_support:
                    boundary.add(v)
                    break
                
        return boundary
    # --------------------------------------------------
    # Graph distance utility
    # --------------------------------------------------
    def graph_distance(self, inter, start, targets, max_depth=50):
        """BFS distance from start to nearest target"""
        if start in targets:
            return 0

        visited = {start}
        frontier = {start}
        depth = 0

        while frontier and depth < max_depth:
            depth += 1
            next_frontier = set()

            for v in frontier:
                for u in inter.get(v, []):
                    if u in visited:
                        continue
                    if u in targets:
                        return depth
                    visited.add(u)
                    next_frontier.add(u)

            frontier = next_frontier

        return float("inf")
    
    
    # --------------------------------------------------
    # Forced probe (Path B)
    # --------------------------------------------------
    def force_second_proto_object(
        self,
        omega_kick=0.3,
        xi_seed=1.0,
        min_distance=10,
    ):
        """
        Inject a second proto-object far from existing ξ support.
        """
    
        inter = worldline_interaction_graph(self.H)
        xi_support = {v for v, x in self.xi.items() if x > 1e-6}
    
        # If no first proto-object exists, abort
        if not xi_support:
            return False
    
        # Candidate vertices: not in ξ
        candidates = [
            v for v in self.H.vertices
            if v not in xi_support
        ]
    
        random.shuffle(candidates)
    
        for v in candidates:
            d = self.graph_distance(inter, v, xi_support)
            if d >= min_distance:
                # Inject Ω defect
                self.defect_log.append({
                    "time": self.time,
                    "birth_time": self.time,
                    "delta_Q": omega_kick,
                    "omega": None,
                    "forced": True,
                    "anchor_vertex": v,
                    "second": True,
                })
    
                # Seed ξ locally
                self.xi[v] = xi_seed
    
                # Temporary nucleation protection
                self.forced_time = self.time
    
                print(
                    f"### SECOND PROBE at t={self.time} | "
                    f"v={v} | dist={d}"
                )
    
                return True
    
        return False

    # --------------------------------------------------
    #--Added function for local omega potential--
    # --------------------------------------------------
    def omega_potential(self, inter, v):
        """
        Pre-closure Ω carrier:
        measures local interaction pressure before loops form
        """
        return len(inter.get(v, []))
    
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
    def _propagate_xi(self, inter, clusters):
        new_xi = dict(self.xi)
        clusters = self.xi_clusters(inter)

        for v, xi_v in self.xi.items():
            if xi_v < 1e-6:
                continue
            
            cid_v = clusters.get(v)
            xi_v = self.XI_DECAY
            
            neighbors = inter.get(v, [])
            for u in neighbors:
                cid_u = clusters.get(u)
                    
                    # Boost intra-cluster coupling
                if cid_u is not None and cid_v is not None and cid_u != cid_v:
                    continue
                    
                new_xi[u] = new_xi.get(u, 0.0) + 0.5 * xi_v / max(len(neighbors), 1)

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
            "xi_support": [
                v for v, x in self.xi.items()
                if x > 1e-6 and v in self.H.vertices
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