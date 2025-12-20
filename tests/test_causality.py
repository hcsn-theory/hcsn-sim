def test_causal_reflexivity():
    from engine.hypergraph import Hypergraph

    H = Hypergraph()
    v = H.add_vertex()

    assert v.id in H.causal_order[v.id]
