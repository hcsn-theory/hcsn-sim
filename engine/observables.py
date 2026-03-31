# engine/observables.py

import random
import math
from dataclasses import dataclass, field


def average_coordination(H):
    return H.average_coordination()


def causal_interval_size(H, u, v):
    future_u = H.causal_future(u)
    past_v = H.causal_past(v)
    return len(future_u.intersection(past_v))


def myrheim_meyer_dimension(H, samples=200, min_interval=10):
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
        d = 2 * math.log(N) / math.log(avg_I)
        return d if math.isfinite(d) else None
    except (ValueError, ZeroDivisionError):
        return None


def average_large_interval(H, samples=50, min_interval=20):
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
    if not H_before.hyperedges:
        return 1.0

    before = {
        tuple(sorted(v.id for v in e.vertices))
        for e in H_before.hyperedges.values()
    }
    after = {
        tuple(sorted(v.id for v in e.vertices))
        for e in H_after.hyperedges.values()
    }

    return len(before & after) / max(len(before), 1)


def interaction_concentration(interactions):
    degrees = [len(v) for v in interactions.values()]
    if not degrees or sum(degrees) == 0:
        return 0.0
    return max(degrees) / sum(degrees)


def worldline_interaction_graph(H, fraction=0.0):
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
    triangles = 0
    for u, nbrs_u in interactions.items():
        for v in nbrs_u:
            if v <= u:
                continue
            nbrs_v = interactions.get(v, set())
            common = nbrs_u & nbrs_v
            for w in common:
                if w > v:
                    triangles += 1
    return triangles


def closure_density(interactions):
    edges = sum(len(nbrs) for nbrs in interactions.values()) // 2
    T = count_triangles(interactions)
    return T / (edges + 1)


def coarse_grain_interactions(H, interactions, scale=2):
    nodes = list(interactions.keys())
    coarse_interactions = {}
    coarse_depths = {}

    blocks = [nodes[i:i + scale] for i in range(0, len(nodes), scale)]

    block_id = {}
    for idx, block in enumerate(blocks):
        for u in block:
            block_id[u] = idx

        depths = [H.vertices[u].depth for u in block if u in H.vertices]
        coarse_depths[idx] = (sum(depths) / len(depths)) if depths else 0.0

    for u, nbrs in interactions.items():
        bu = block_id[u]
        coarse_interactions.setdefault(bu, set())
        for v in nbrs:
            bv = block_id[v]
            if bu != bv:
                coarse_interactions[bu].add(bv)

    return coarse_interactions, coarse_depths


def hierarchical_closure(H, interactions, scales=(2, 4, 8)):
    psi_vals = []
    current = interactions

    for s in scales:
        coarse_inter, _ = coarse_grain_interactions(H, current, scale=s)
        psi_vals.append(closure_density(coarse_inter))
        current = coarse_inter

    if not psi_vals:
        return 0.0

    return min(psi_vals)


def loop_mismatch_weights(interactions, depths, beta=0.05):
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
                    var_t = ((tu - mean_t) ** 2 + (tv - mean_t) ** 2 + (tw - mean_t) ** 2) / 3

                    theta = base * (1 + beta * var_t)
                    weights.append(theta)

    return weights


def emergent_distance_scale(interactions, depths, beta=0.05):
    weights = loop_mismatch_weights(interactions, depths, beta)
    if not weights:
        return 0.0
    return sum(weights) / len(weights)


def renormalized_distance_scales(H, interactions, depths, beta=0.05, scales=(2, 4, 8, 16)):
    results = {}
    current_inter = interactions
    _current_depths = depths

    for s in scales:
        coarse_inter, coarse_depths = coarse_grain_interactions(H, current_inter, scale=s)
        results[s] = emergent_distance_scale(coarse_inter, coarse_depths, beta)
        current_inter = coarse_inter
        _current_depths = coarse_depths

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


def local_omega(H, inter, v):
    neighbors = inter.get(v, [])
    if not neighbors:
        return 0.0

    closed = 0
    for u in neighbors:
        if u in inter and v in inter[u]:
            closed += 1

    return closed / max(len(neighbors), 1)


def compute_coherence_raw(neighborhood, inter):
    internal = 0
    boundary = 0
    for n in neighborhood:
        for nn in inter.get(n, []):
            if nn in neighborhood:
                internal += 1
            else:
                boundary += 1
    return internal // 2, boundary


@dataclass
class TopologicalKnot:
    id: int
    vertices: set
    age: int
    max_size: int
    min_size: int
    radius: float
    coherence: float
    velocity: float
    velocity_avg: tuple
    mass: float
    momentum: float
    position_history: list = field(default_factory=list)


@dataclass
class InteractionEvent:
    time: int
    knot_a: int
    knot_b: int
    overlap_size: int
    overlap_depth: float
    resonance: float
    pre_a: tuple
    pre_b: tuple
    post_a: tuple = None
    post_b: tuple = None

    def to_dict(self):
        return {
            "time": self.time,
            "knot_a": self.knot_a,
            "knot_b": self.knot_b,
            "overlap_size": self.overlap_size,
            "overlap_depth": self.overlap_depth,
            "resonance": self.resonance,
            "pre_a": list(self.pre_a),
            "pre_b": list(self.pre_b),
            "post_a": list(self.post_a) if self.post_a is not None else None,
            "post_b": list(self.post_b) if self.post_b is not None else None,
        }


def component_radius(comp, inter):
    if len(comp) < 2:
        return 0.0

    total_dist = 0
    pairs = 0

    for start in comp:
        visited = {start}
        queue = [(start, 0)]
        head = 0

        while head < len(queue):
            node, dist = queue[head]
            head += 1

            total_dist += dist
            if dist > 0:
                pairs += 1

            for nbr in inter.get(node, []):
                if nbr in comp and nbr not in visited:
                    visited.add(nbr)
                    queue.append((nbr, dist + 1))

    return (total_dist / pairs) if pairs > 0 else 0.0


def local_clustering(inter, v):
    nbrs = inter.get(v)
    if not nbrs or len(nbrs) < 2:
        return 0.0

    links = 0
    for u in nbrs:
        u_nbrs = inter.get(u, set())
        for w in nbrs:
            if u != w and w in u_nbrs:
                links += 1

    possible = len(nbrs) * (len(nbrs) - 1)
    return links / possible if possible > 0 else 0.0


def detect_candidate_knots(H, inter, min_coherence):
    theta_comp = 0.6
    seed_regions = []

    for v in H.vertices.keys():
        neighbors = inter.get(v)
        if not neighbors:
            continue

        neighborhood = set(neighbors)
        neighborhood.add(v)

        if len(neighborhood) < 3:
            continue

        internal, boundary = compute_coherence_raw(neighborhood, inter)

        if boundary > 0:
            coherence = internal / boundary
        elif internal > 0:
            coherence = 10.0
        else:
            coherence = 0.0

        total = internal + boundary
        compactness = (internal / total) if total > 0 else 0.0

        if coherence > min_coherence and compactness > theta_comp:
            seed_regions.append(neighborhood)

    if not seed_regions:
        return []

    merged = []
    used = [False] * len(seed_regions)

    for i in range(len(seed_regions)):
        if used[i]:
            continue

        used[i] = True
        cluster = set(seed_regions[i])

        changed = True
        while changed:
            changed = False
            for j in range(len(seed_regions)):
                if used[j]:
                    continue

                overlap = len(cluster.intersection(seed_regions[j]))
                min_size = min(len(cluster), len(seed_regions[j]))
                if min_size > 0 and (overlap / min_size) > 0.3:
                    cluster.update(seed_regions[j])
                    used[j] = True
                    changed = True

        merged.append(cluster)

    return merged
