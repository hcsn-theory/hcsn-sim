import json
import numpy as np
import matplotlib.pyplot as plt

def main():
    with open("analysis/defect_momentum_timeseries.json") as f:
        data = json.load(f)

    lifetimes = []
    variances = []

    for d in data:
        tau = d["samples"]
        var_p = d["var_p"]

        if tau > 0 and var_p > 0:
            lifetimes.append(tau)
            variances.append(var_p)

    lifetimes = np.array(lifetimes)
    variances = np.array(variances)

    # --- log-log fit ---
    log_tau = np.log(lifetimes)
    log_var = np.log(variances)

    slope, intercept = np.polyfit(log_tau, log_var, 1)
    alpha = -slope

    print("\n=== Lifetime–Momentum Scaling ===")
    print(f"Samples: {len(lifetimes)}")
    print(f"Scaling exponent α ≈ {alpha:.3f}")
    print(f"Fit: Var(p) ~ τ^(-{alpha:.3f})")

    # --- plot ---
    plt.figure(figsize=(7, 5))
    plt.scatter(lifetimes, variances, s=60, alpha=0.8, label="defects")

    # fitted line
    tau_fit = np.linspace(lifetimes.min(), lifetimes.max(), 200)
    var_fit = np.exp(intercept) * tau_fit ** (-alpha)

    plt.plot(tau_fit, var_fit, "--", label=f"fit α={alpha:.2f}")

    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Lifetime τ (samples)")
    plt.ylabel("Momentum variance Var(p)")
    plt.title("Emergent Uncertainty: Lifetime vs Momentum Variance")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()