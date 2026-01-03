# analysis/test_linear_response.py
import json
import numpy as np

with open("analysis/omega_timeseries.json") as f:
    data = json.load(f)

omega = np.array([d["omega"] for d in data])
dt = np.diff(omega)

# Linear predictor: ΔΩ(t+1) ≈ a ΔΩ(t)
x = dt[:-1]
y = dt[1:]

a = np.dot(x, y) / np.dot(x, x)
residual = y - a * x

print("Linear response coefficient a =", a)
print("Residual variance =", np.var(residual))