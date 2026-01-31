import json
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import linregress

# ---------- models ----------
def exp_model(O, A, a):
    return A * np.exp(-a * O)

def power_model(O, B, b):
    return B * O**(-b)

def critical_model(O, C, Oc, nu):
    return C * (Oc - O)**nu

# ---------- load binned data ----------
with open("analysis/defect_rate_vs_omega_bins.json") as f:
    data = json.load(f)

# Filter valid entries FIRST
filtered = [
    d for d in data
    if d["rate"] is not None and np.isfinite(d["rate"]) and d["rate"] > 0
]

Omega = np.array([d["omega"] for d in filtered])
rate  = np.array([d["rate"]  for d in filtered])


print("\n=== Defect Rate Suppression Fits ===")

# ---------- exponential ----------
popt_exp, _ = curve_fit(exp_model, Omega, rate, maxfev=10000)
A, a = popt_exp
res_exp = np.mean((rate - exp_model(Omega, *popt_exp))**2)

print("\n[Exponential]")
print(f"A ≈ {A:.3e}, a ≈ {a:.3f}")
print(f"MSE ≈ {res_exp:.3e}")

# ---------- power law ----------
logO = np.log(Omega)
logR = np.log(rate)
slope, intercept, r, p, _ = linregress(logO, logR)
b = -slope
B = np.exp(intercept)
res_pow = np.mean((rate - power_model(Omega, B, b))**2)

print("\n[Power law]")
print(f"B ≈ {B:.3e}, b ≈ {b:.3f}")
print(f"MSE ≈ {res_pow:.3e}")

# ---------- critical ----------
try:
    popt_crit, _ = curve_fit(
        critical_model,
        Omega,
        rate,
        bounds=([0, max(Omega), 0], [np.inf, 2*max(Omega), 5]),
        maxfev=20000
    )
    C, Oc, nu = popt_crit
    res_crit = np.mean((rate - critical_model(Omega, *popt_crit))**2)

    print("\n[Critical]")
    print(f"C ≈ {C:.3e}, Ωc ≈ {Oc:.3f}, ν ≈ {nu:.3f}")
    print(f"MSE ≈ {res_crit:.3e}")

except RuntimeError:
    res_crit = np.inf
    print("\n[Critical] Fit failed")

# ---------- verdict ----------
print("\n=== Model Comparison ===")
print(f"Exponential MSE: {res_exp:.3e}")
print(f"Power-law  MSE: {res_pow:.3e}")
print(f"Critical   MSE: {res_crit:.3e}")

best = min(
    [("Exponential", res_exp), ("Power-law", res_pow), ("Critical", res_crit)],
    key=lambda x: x[1]
)
print(f"\nBEST FIT: {best[0]}")