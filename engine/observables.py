# engine/observables.py

import random
import math


def average_coordination(H):
    """
    Compute average coordination number <k>.
    """
    return H.average_coordination()


def causal_interval_size(H, u, v):
    """
    |I(u, v)| = |J+(u) ∩ J-(v)|
    """
    future_u = H.causal_future(u)
    past_v = H.causal_past(v)
    return len(future_u.intersection(past_v))


def myrheim_meyer_dimension(H, samples=200, min_interval=10):
    """
    Myrheim–Meyer dimension estimator with interval filtering.
    Only considers sufficiently large causal intervals.
    """

    vertices = list(H.vertices.values())
    if len(vertices) < 2:
        return None

    sizes = []

    for _ in range(samples):
        u, v = random.sample(vertices, 2)
        if H.is_causally_related(u, v):
            I = causal_interval_size(H, u, v)
            if I >= min_interval:
                sizes.append(I)

    if not sizes:
        return None

    avg_I = sum(sizes) / len(sizes)
    N = len(H.vertices)

    if avg_I <= 1:
        return None

    try:
        return 2 * math.log(N) / math.log(avg_I)
    except (ValueError, ZeroDivisionError):
        return None

def average_large_interval(H, samples=50, min_interval=20):
    """
    Measure average size of large causal intervals.
    Returns 0 if none exist.
    """
    vertices = list(H.vertices.values())
    if len(vertices) < 2:
        return 0.0

    sizes = []
    for _ in range(samples):
        u, v = random.sample(vertices, 2)
        if H.is_causally_related(u, v):
            I = causal_interval_size(H, u, v)
            if I >= min_interval:
                sizes.append(I)

    if not sizes:
        return 0.0

    return sum(sizes) / len(sizes)

def adjacency_overlap(H_before, H_after):
    """
    Fraction of hyperedges that persist after a rewrite.
    """
    if not H_before.hyperedges:
        return 1.0

    before = {tuple(sorted(v.id for v in e.vertices))
              for e in H_before.hyperedges.values()}
    after = {tuple(sorted(v.id for v in e.vertices))
             for e in H_after.hyperedges.values()}

    return len(before & after) / max(len(before), 1)

def interaction_concentration(interactions):
    """
    Φ = max degree / total degree
    interactions: dict {node_id: set(neighbors)}
    """
    degrees = [len(v) for v in interactions.values()]
    if not degrees or sum(degrees) == 0:
        return 0.0
    return max(degrees) / sum(degrees)

def worldline_interaction_graph(H, fraction=0.6):
    """
    Build interaction graph among deep worldlines.
    """
    from collections import defaultdict

    max_depth = H.max_chain_length()
    cutoff = int(fraction * max_depth)

    worldlines = [v for v in H.vertices.values() if v.depth >= cutoff]
    wl_ids = {v.id for v in worldlines}

    interactions = defaultdict(set)

    for edge in H.hyperedges.values():
        ids = [v.id for v in edge.vertices if v.id in wl_ids]
        for i in ids:
            for j in ids:
                if i != j:
                    interactions[i].add(j)

    return interactions

def count_triangles(interactions):
    """
    Count triangles in an undirected interaction graph.
    interactions: dict {node_id: set(neighbors)}
    """
    triangles = 0
    for u, nbrs_u in interactions.items():
        for v in nbrs_u:
            if v <= u:
                continue
            nbrs_v = interactions.get(v, set())
            # common neighbors w form triangles u-v-w
            common = nbrs_u & nbrs_v
            for w in common:
                if w > v:
                    triangles += 1
    return triangles


def closure_density(interactions):
    """
    Ψ = T / (E + 1)
    T: number of triangles
    E: number of edges
    """
    # count edges once
    edges = sum(len(nbrs) for nbrs in interactions.values()) // 2
    T = count_triangles(interactions)
    return T / (edges + 1)

def coarse_grain_interactions(H, interactions, scale=2):
    """
    Coarse-grain interaction graph by grouping nodes.
    Returns:
        coarse_interactions: dict
        coarse_depths: dict (effective time field)
    """
    nodes = list(interactions.keys())
    coarse_interactions = {}
    coarse_depths = {}

    # partition nodes into blocks
    blocks = [
        nodes[i:i + scale]
        for i in range(0, len(nodes), scale)
    ]

    block_id = {}
    for idx, block in enumerate(blocks):
        for u in block:
            block_id[u] = idx

        # effective time = mean depth
        depths = [
            H.vertices[u].depth
            for u in block
            if u in H.vertices
        ]
        if depths:
            coarse_depths[idx] = sum(depths) / len(depths)
        else:
            coarse_depths[idx] = 0.0

    # build coarse interaction graph
    for u, nbrs in interactions.items():
        bu = block_id[u]
        coarse_interactions.setdefault(bu, set())

        for v in nbrs:
            bv = block_id[v]
            if bu != bv:
                coarse_interactions[bu].add(bv)

    return coarse_interactions, coarse_depths


def hierarchical_closure(H, interactions, scales=(2, 4, 8)):
    """
    Measure stability of closure under coarse-graining.
    RG-aware: unpacks (interactions, depths) tuples.
    """
    from engine.observables import coarse_grain_interactions, closure_density

    psi_vals = []
    current = interactions

    for s in scales:
        result = coarse_grain_interactions(H, current, scale=s)

        # RG-aware unpacking
        if isinstance(result, tuple):
            coarse_inter, _ = result
        else:
            coarse_inter = result

        psi_vals.append(closure_density(coarse_inter))
        current = coarse_inter

    if not psi_vals:
        return 0.0

    return min(psi_vals)
def loop_mismatch_weights(interactions, depths, beta=0.05):
    """
    Protected metric mismatch: degree mismatch × time variance.
    """
    degrees = {u: len(vs) for u, vs in interactions.items()}
    if not degrees:
        return []

    avg_d = sum(degrees.values()) / len(degrees)
    weights = []

    for u, nbrs_u in interactions.items():
        for v in nbrs_u:
            if v <= u:
                continue
            nbrs_v = interactions.get(v, set())
            common = nbrs_u & nbrs_v
            for w in common:
                if w > v:
                    du, dv, dw = degrees[u], degrees[v], degrees[w]
                    base = abs((du + dv + dw) - 3 * avg_d)

                    tu = depths.get(u, 0.0)
                    tv = depths.get(v, 0.0)
                    tw = depths.get(w, 0.0)

                    mean_t = (tu + tv + tw) / 3
                    var_t = ((tu - mean_t)**2 +
                             (tv - mean_t)**2 +
                             (tw - mean_t)**2) / 3

                    theta = base * (1 + beta * var_t)
                    weights.append(theta)

    return weights

def emergent_distance_scale(interactions, depths, beta=0.05):
    """
    Emergent metric scale with time-protected mismatch.
    """
    weights = loop_mismatch_weights(interactions, depths, beta)
    if not weights:
        return 0.0
    return sum(weights) / len(weights)

def renormalized_distance_scales(H, interactions, depths,
                                 beta=0.05, scales=(2, 4, 8, 16)):
    """
    Compute protected emergent distance scale under coarse-graining.
    """
    results = {}
    current_inter = interactions
    current_depths = depths

    for s in scales:
        coarse_inter, coarse_depths = coarse_grain_interactions(
            H, current_inter, scale=s
        )
        results[s] = emergent_distance_scale(
            coarse_inter, coarse_depths, beta
        )
        current_inter = coarse_inter
        current_depths = coarse_depths

    return results
 
def label_frustration(H):
    mismatches = 0
    for edge in H.hyperedges.values():
        labels = {v.label for v in edge.vertices}
        if len(labels) > 1:
            mismatches += 1
    return mismatches

def defect_density(H):
    if len(H.hyperedges) == 0:
        return 0.0
    return label_frustration(H) / len(H.hyperedges)


def local_hierarchical_closure(H, inter, v_id, radius=2):
    
    #Local hierarchical closure around vertex v_id.
    
    # 1. Find neighborhood
    frontier = {v_id}
    visited = {v_id}

    for _ in range(radius):
        new = set()
        for u in frontier:
            for w in inter.neighbors(u):
                if w not in visited:
                    visited.add(w)
                    new.add(w)
        frontier = new

    if len(visited) < 3:
        return 0.0

    # 2. Induce subgraph
    sub_vertices = {vid: H.vertices[vid] for vid in visited if vid in H.vertices}
    sub_inter = inter.subgraph(visited)

    # 3. Measure hierarchy locally
    return hierarchical_closure(
        H.from_subgraph(sub_vertices, sub_inter),
        sub_inter
    )
     
def local_omega(H, inter, v):
    """
    Local contribution to hierarchical closure.
    Proxy: fraction of interactions involving v that participate in closure.
    """
    neighbors = inter.get(v, [])
    if not neighbors:
        return 0.0

    closed = 0
    for u in neighbors:
        if u in inter and v in inter[u]:
            closed += 1

    return closed / max(len(neighbors), 1)