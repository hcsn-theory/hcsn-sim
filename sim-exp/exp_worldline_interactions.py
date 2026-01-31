from collections import defaultdict
from engine.hypergraph import Hypergraph
from engine.rewrite_engine import RewriteEngine


def extract_worldlines(H, fraction=0.6):
    """
    Identify worldline vertices by depth threshold.
    """
    max_depth = H.max_chain_length()
    cutoff = int(fraction * max_depth)

    worldline_vertices = [
        v for v in H.vertices.values() if v.depth >= cutoff
    ]
    return worldline_vertices


def build_interaction_graph(H, worldline_vertices):
    """
    Build a graph where nodes are worldlines
    and edges indicate shared hyperedges.
    """
    interactions = defaultdict(set)

    worldline_set = set(v.id for v in worldline_vertices)

    for edge in H.hyperedges.values():
        ids = [v.id for v in edge.vertices if v.id in worldline_set]
        for i in ids:
            for j in ids:
                if i != j:
                    interactions[i].add(j)

    return interactions


def main():
    # Re-run universe (same parameters)
    H = Hypergraph()
    v1 = H.add_vertex()
    v2 = H.add_vertex()
    H.add_causal_relation(v1, v2)
    H.add_hyperedge([v1, v2])

    engine = RewriteEngine(
        H,
        p_create=0.5,
        seed=2,
        gamma_time=0.1,
        gamma_space=0.1
    )

    engine.run(40000)

    worldlines = extract_worldlines(H, fraction=0.6)
    interactions = build_interaction_graph(H, worldlines)

    print("Number of worldline vertices:", len(worldlines))

    degrees = [len(interactions[v.id]) for v in worldlines]

    if degrees:
        print("Avg worldline degree:", sum(degrees) / len(degrees))
        print("Max worldline degree:", max(degrees))
        print("Min worldline degree:", min(degrees))
    else:
        print("No interactions found.")


if __name__ == "__main__":
    main()
