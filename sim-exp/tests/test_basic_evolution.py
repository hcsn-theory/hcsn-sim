from engine.hypergraph import Hypergraph
from engine.rewrite_engine import RewriteEngine

def test_universe_evolves_without_crashing():
    H = Hypergraph()
    v1 = H.add_vertex()
    v2 = H.add_vertex()
    H.add_causal_relation(v1, v2)
    H.add_hyperedge([v1, v2])

    engine = RewriteEngine(H, seed=0)

    for _ in range(500):
        engine.step()

    assert len(H.vertices) > 2
