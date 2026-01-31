import json
import numpy as np
import matplotlib.pyplot as plt

# =============================
# Configuration
# =============================
TIMESERIES_FILE = "timeseries.json"
WINDOW_SIZE = 500        # rewrite steps
MIN_DEFECTS = 1          # require at least this many defects per window

# =============================
# Load data
# =============================
with open(TIMESERIES_FILE, "r") as f:
    data = json.load(f)

# Support both single-run and multi-run formats
if isinstance(data, list):
    run = data[-1]
elif isinstance(data, dict) and "runs" in data:
    run = data["runs"][-1]
else:
    run = data

t = np.array(run["t"])
omega = np.array(run["omega"])
defects = run.get("defects", [])

defect_times = np.array([d["time"] for d in defects])

# =============================
# Sliding windows
# =============================
t_min = t.min()
t_max = t.max()

window_starts = np.arange(t_min, t_max - WINDOW_SIZE, WINDOW_SIZE)

rates = []
variances = []

for start in window_starts:
    end = start + WINDOW_SIZE

    # Ω samples in window
    mask = (t >= start) & (t < end)
    if mask.sum() < 3:
        continue

    omega_window = omega[mask]
    var_omega = np.var(omega_window)

    # Defects in window
    n_defects = np.sum((defect_times >= start) & (defect_times < end))
    if n_defects < MIN_DEFECTS:
        continue

    defect_rate = n_defects / WINDOW_SIZE

    rates.append(defect_rate)
    variances.append(var_omega)

rates = np.array(rates)
variances = np.array(variances)

# =============================
# Sanity check
# =============================
print(f"Parsed windows: {len(rates)}")
if len(rates) == 0:
    raise RuntimeError("No valid windows found — increase WINDOW_SIZE or lower MIN_DEFECTS")

# =============================
# Plot
# =============================
plt.figure(figsize=(7, 6))

plt.scatter(
    variances,
    rates,
    s=50,
    alpha=0.75,
    edgecolor="k"
)

plt.xscale("log")
plt.yscale("log")

plt.xlabel("Var(Ω)  (sliding window)")
plt.ylabel("Defect rate  (per step)")
plt.title("Defect Rate vs Geometric Fluctuation")

plt.grid(alpha=0.3, which="both")
plt.tight_layout()
plt.show()
