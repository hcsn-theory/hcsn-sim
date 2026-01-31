def test_coordination_remains_bounded():
    from engine.hypergraph import Hypergraph
    from engine.rewrite_engine import RewriteEngine

    H = Hypergraph()
    v1 = H.add_vertex()
    v2 = H.add_vertex()
    H.add_causal_relation(v1, v2)
    H.add_hyperedge([v1, v2])

    engine = RewriteEngine(H, seed=1)

    for _ in range(1000):
        engine.step()

    k = H.average_coordination()
    assert k < 15
