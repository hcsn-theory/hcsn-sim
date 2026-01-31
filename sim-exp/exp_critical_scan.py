# experiments/exp_critical_scan.py

from engine.hypergraph import Hypergraph
from engine.rewrite_engine import RewriteEngine
from engine.observables import average_coordination, myrheim_meyer_dimension


def run_universe(p_create, steps=10000, seed=0):
    H = Hypergraph()

    v1 = H.add_vertex()
    v2 = H.add_vertex()
    H.add_causal_relation(v1, v2)
    H.add_hyperedge([v1, v2])

    engine = RewriteEngine(H, p_create=p_create, seed=seed)
    engine.run(steps)

    k_avg = average_coordination(H)
    dim = myrheim_meyer_dimension(H, samples=800, min_interval=20)

    return len(H.vertices), k_avg, dim


def main():
    print("p_create | vertices | <k>    | dimension")
    print("------------------------------------------")

    for p in [0.47, 0.48, 0.49, 0.50, 0.51, 0.52, 0.53]:
        vertices, k_avg, dim = run_universe(
            p_create=p,
            steps=10000,
            seed=1
        )

        dim_str = f"{dim:.2f}" if dim is not None else "None"

        print(
            f"{p:7.2f} | "
            f"{vertices:8d} | "
            f"{k_avg:6.2f} | "
            f"{dim_str}"
        )


if __name__ == "__main__":
    main()
