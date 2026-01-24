# engine/rules.py

import random


def edge_creation_rule(H, anchor_vertex=None):

    if not H.hyperedges:
        return None

    undo = {
        "added_vertices": [],
        "added_edges": [],
        "added_causal": []
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

    new_vertex = H.add_vertex()
    undo["added_vertices"].append(new_vertex.id)

    # connect causally to vertices in the chosen edge
    for v in edge.vertices:
        H.add_causal_relation(v, new_vertex)
        undo["added_causal"].append((v.id, new_vertex.id))

    # causal thickening
    for v in edge.vertices:
        for u in H.causal_past(v):
            if random.random() < 0.3:
                H.add_causal_relation(u, new_vertex)
                undo["added_causal"].append((u.id, new_vertex.id))

    # create new hyperedge
    e = H.add_hyperedge(list(edge.vertices) + [new_vertex])
    undo["added_edges"].append(e.id)

    return undo

def vertex_fusion_rule(H):
    
    if len(H.vertices) < 3 or len(H.hyperedges) < 1:
        return None

    edge = random.choice(list(H.hyperedges.values()))
    
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
        "removed_edges": {},
        "old_causal": {}
    }

    # log causal relations
    for u in H.vertices.values():
        if v_remove.id in H.causal_order[u.id]:
            undo["old_causal"][u.id] = set(H.causal_order[u.id])

    # redirect causal relations
    for u in H.vertices.values():
        if v_remove.id in H.causal_order[u.id]:
            H.causal_order[u.id].add(v_keep.id)
            H.causal_order[u.id].discard(v_remove.id)

    # remove edges containing v_remove
    for eid in list(H.hyperedges.keys()):
        e = H.hyperedges[eid]
        if v_remove in e.vertices:
            undo["removed_edges"][eid] = e
            del H.hyperedges[eid]

    # remove vertex
    del H.vertices[v_remove.id]
    del H.causal_order[v_remove.id]

    return undo