import json
import numpy as np
from scipy.optimize import curve_fit

# ----------------------------
# Load Ωc extraction results
# ----------------------------
with open("analysis/omega_c_by_variant.json") as f:
    omega_data = json.load(f)

# ----------------------------
# Load run lengths
# ----------------------------
with open("timeseries.json") as f:
    runs = json.load(f)["runs"]

# Match runs
Omega_c = []
L = []

for entry in omega_data:
    i = entry["run_index"]
    Omega_c.append(entry["Omega_c"])
    L.append(runs[i]["t"][-1])   # total runtime as size proxy

Omega_c = np.array(Omega_c)
L = np.array(L)

# ----------------------------
# Finite-size scaling model
# Ωc(L) = Ω∞ + a * L^{-b}
# ----------------------------
def scaling_model(L, Omega_inf, a, b):
    return Omega_inf + a * L**(-b)

# Initial guess
p0 = [np.mean(Omega_c), 1.0, 0.5]

popt, pcov = curve_fit(scaling_model, L, Omega_c, p0=p0, maxfev=20000)
Omega_inf, a, b = popt

# Residuals
res = np.mean((Omega_c - scaling_model(L, *popt))**2)

print("\n=== Finite-Size Scaling of Ωc ===")
print(f"Ωc(∞) ≈ {Omega_inf:.4f}")
print(f"Scaling exponent b ≈ {b:.3f}")
print(f"Residual MSE ≈ {res:.3e}")

# ----------------------------
# Sanity check: monotonic drift
# ----------------------------
order = np.argsort(L)
corr = np.corrcoef(L[order], Omega_c[order])[0, 1]

print(f"Corr(Ωc, size) ≈ {corr:.3f}")