# engine/rules.py

import random


def edge_creation_rule(H, anchor_vertex=None, p_rule=0.03):
    if not H.hyperedges:
        return None

    undo = {
        "added_vertices": [],
        "added_edges": [],
        "added_causal": [],
    }

    if anchor_vertex is None:
        edge = random.choice(list(H.hyperedges.values()))
    else:
        candidates = [
            e for e in H.hyperedges.values()
            if anchor_vertex in e.vertices
        ]
        if not candidates:
            return None
        edge = random.choice(candidates)

    # Loop closure with existing vertices.
    if random.random() < p_rule and len(H.vertices) >= 3:
        u, v = random.sample(list(H.vertices.values()), 2)
        if not H.is_causally_related(u, v):
            H.add_causal_relation(u, v)
            e = H.add_hyperedge([u, v])
            undo["added_edges"].append(e.id)
            undo["added_causal"].append((u.id, v.id))

    new_vertex = H.add_vertex()
    undo["added_vertices"].append(new_vertex.id)

    for v in edge.vertices:
        H.add_causal_relation(v, new_vertex)
        undo["added_causal"].append((v.id, new_vertex.id))

    for v in edge.vertices:
        for u in H.causal_past(v):
            if random.random() < 0.3:
                H.add_causal_relation(u, new_vertex)
                undo["added_causal"].append((u.id, new_vertex.id))

    e = H.add_hyperedge(list(edge.vertices) + [new_vertex])
    undo["added_edges"].append(e.id)

    return undo


def vertex_fusion_rule(H, anchor_vertex=None):
    if len(H.vertices) < 3 or len(H.hyperedges) < 1:
        return None

    if anchor_vertex is None:
        edge = random.choice(list(H.hyperedges.values()))
    else:
        candidates = [
            e for e in H.hyperedges.values()
            if anchor_vertex in e.vertices
        ]
        if not candidates:
            return None
        edge = random.choice(candidates)

    if len(edge.vertices) < 3:
        return None

    v_keep = edge.vertices[0]
    v_remove = edge.vertices[1]

    remaining_edges = [
        e for e in H.hyperedges.values()
        if v_remove not in e.vertices
    ]
    if not remaining_edges:
        return None

    undo = {
        "removed_vertex": v_remove,
        "kept_vertex": v_keep,
        "removed_edges": {},
        "old_causal": {},
    }

    for u in H.vertices.values():
        if v_remove.id in H.causal_order[u.id]:
            undo["old_causal"][u.id] = set(H.causal_order[u.id])

    for u in H.vertices.values():
        if v_remove.id in H.causal_order[u.id]:
            H.causal_order[u.id].add(v_keep.id)
            H.causal_order[u.id].discard(v_remove.id)

    for eid in list(H.hyperedges.keys()):
        e = H.hyperedges[eid]
        if v_remove in e.vertices:
            undo["removed_edges"][eid] = e
            del H.hyperedges[eid]

    del H.vertices[v_remove.id]
    del H.causal_order[v_remove.id]

    return undo
