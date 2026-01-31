# experiments/exp_phase_diagram.py

from engine.hypergraph import Hypergraph
from engine.rewrite_engine import RewriteEngine
from engine.observables import average_coordination, myrheim_meyer_dimension


def run_experiment(p_create, steps=8000, seed=0):
    """
    Run a single universe for given p_create.
    """
    H = Hypergraph()

    v1 = H.add_vertex()
    v2 = H.add_vertex()
    H.add_causal_relation(v1, v2)
    H.add_hyperedge([v1, v2])

    engine = RewriteEngine(H, p_create=p_create, seed=seed)
    engine.run(steps)

    k_avg = average_coordination(H)
    dim = myrheim_meyer_dimension(H, samples=500, min_interval=15)

    return len(H.vertices), k_avg, dim


def main():
    print("p_create | vertices | <k>    | dimension")
    print("------------------------------------------")

    for p in [0.45, 0.50, 0.55, 0.58, 0.60, 0.62, 0.65, 0.68]:
        vertices, k_avg, dim = run_experiment(
            p_create=p,
            steps=8000,
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
