import json
import numpy as np
from sklearn.linear_model import LinearRegression

DT = 100  # your logging interval

def second_derivative(x):
    return x[2:] - 2*x[1:-1] + x[:-2]

def main():
    with open("analysis/omega_timeseries.json") as f:
        data = json.load(f)

    omega = np.array([d["omega"] for d in data])

    # --- time derivatives ---
    d2omega = second_derivative(omega)

    # --- proxy spatial Laplacian ---
    # (coarse-grained topological diffusion)
    laplace = omega[2:] - omega[1:-1]

    # --- align ---
    y = d2omega
    X = np.column_stack([laplace, -omega[1:-1]])

    model = LinearRegression(fit_intercept=False)
    model.fit(X, y)

    c2, m2 = model.coef_

    print("\n=== Step 20.3: Effective Ω Equation ===")
    print(f"c_Ω² ≈ {c2:.6f}")
    print(f"m_Ω² ≈ {m2:.6f}")
    print(f"R²    ≈ {model.score(X, y):.3f}")

    out = {
        "c_omega_sq": float(c2),
        "m_omega_sq": float(m2),
        "r_squared": float(model.score(X, y))
    }

    with open("analysis/effective_eom.json", "w") as f:
        json.dump(out, f, indent=2)

    print("Saved effective Ω equation to analysis/effective_eom.json")

if __name__ == "__main__":
    main()