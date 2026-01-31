# experiments/exp_long_critical_run.py

from engine.hypergraph import Hypergraph
from engine.rewrite_engine import RewriteEngine
from engine.observables import average_coordination, myrheim_meyer_dimension


def run_long(p_create=0.50, steps=50000, seed=1):
    H = Hypergraph()

    v1 = H.add_vertex()
    v2 = H.add_vertex()
    H.add_causal_relation(v1, v2)
    H.add_hyperedge([v1, v2])

    engine = RewriteEngine(H, p_create=p_create, seed=seed)
    engine.run(steps)

    k_avg = average_coordination(H)
    dim = myrheim_meyer_dimension(H, samples=2000, min_interval=30)

    return len(H.vertices), k_avg, dim


if __name__ == "__main__":
    vertices, k_avg, dim = run_long()

    print("Critical long run")
    print("-----------------")
    print("Vertices =", vertices)
    print("<k> =", k_avg)
    print("Estimated dimension =", dim)
