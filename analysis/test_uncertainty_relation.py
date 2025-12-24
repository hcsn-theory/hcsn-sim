import json
import numpy as np
import matplotlib.pyplot as plt

def main():
    with open("timeseries.json") as f:
        data = json.load(f)

    run = data["runs"][-1]
    defects = run["defects"]

    lifetimes = []
    variances = []

    for d in defects:
        if "momentum_series" not in d:
            continue

        p = np.array(d["momentum_series"])
        if len(p) < 3:
            continue

        lifetimes.append(d["lifetime"])
        variances.append(np.var(p))

    lifetimes = np.array(lifetimes)
    variances = np.array(variances)

    if len(lifetimes) == 0:
        print("No data for uncertainty test.")
        return

    product = lifetimes * variances

    print("\n=== Uncertainty-like Relation ===")
    print(f"Mean τ·Var(p): {product.mean():.3f}")
    print(f"Std τ·Var(p):  {product.std():.3f}")
    print(f"Correlation (τ vs Var(p)): {np.corrcoef(lifetimes, variances)[0,1]:.3f}")

    plt.scatter(lifetimes, variances)
    plt.xlabel("Lifetime τ")
    plt.ylabel("Var(p)")
    plt.title("Lifetime–Momentum Variance Tradeoff")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()