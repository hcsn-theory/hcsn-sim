import json
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------------
# Load latest run from timeseries.json
# -------------------------------------------------
with open("timeseries.json", "r") as f:
    data = json.load(f)

# Handle both formats (list-only or runs-wrapped)
if isinstance(data, list):
    run = data[-1]
else:
    run = data["runs"][-1]

t = np.array(run["t"])
omega = np.array(run["omega"])
defects = run.get("defects", [])

if len(defects) < 2:
    raise RuntimeError("Not enough defects for statistics")

# -------------------------------------------------
# Helper: interpolate Ω(t) at arbitrary time
# -------------------------------------------------
def omega_at(time):
    return np.interp(time, t, omega)

# =================================================
# 1. ΔΩ vs ΔQ
# =================================================
delta_Q = []
delta_omega = []

for d in defects:
    tq = d["time"]
    dq = d["delta_Q"]

    # Ω just before and after defect
    eps = 1e-6
    o_before = omega_at(tq - eps)
    o_after  = omega_at(tq + eps)

    delta_Q.append(dq)
    delta_omega.append(o_after - o_before)

# =================================================
# 2. Defect spacing histogram
# =================================================
defect_times = np.array([d["time"] for d in defects])
spacings = np.diff(defect_times)

# =================================================
# 3. Sliding-window Ω variance
# =================================================
window = 10  # number of samples (not steps)
omega_var = [
    np.var(omega[i:i+window])
    for i in range(len(omega) - window)
]
t_var = t[:len(omega_var)]

# =================================================
# 4. Coarse-grained Ω(scale)
# =================================================
scales = [1, 2, 4, 8, 16, 32]
omega_scale = []

for s in scales:
    blocks = len(omega) // s
    blocked = omega[:blocks*s].reshape(blocks, s)
    omega_scale.append(blocked.mean())

# =================================================
# Plotting
# =================================================
fig, axs = plt.subplots(2, 2, figsize=(14, 10))

# ---- ΔΩ vs ΔQ ----
axs[0, 0].scatter(delta_Q, delta_omega, s=50)
axs[0, 0].axhline(0, linestyle="--", alpha=0.4)
axs[0, 0].axvline(0, linestyle="--", alpha=0.4)
axs[0, 0].set_xlabel("Defect charge ΔQ")
axs[0, 0].set_ylabel("Ω jump ΔΩ")
axs[0, 0].set_title("Defect Response: ΔΩ vs ΔQ")

# ---- Defect spacing histogram ----
axs[0, 1].hist(spacings, bins=15, edgecolor="black")
axs[0, 1].set_xlabel("Defect spacing (steps)")
axs[0, 1].set_ylabel("Count")
axs[0, 1].set_title("Defect Spacing Distribution")

# ---- Sliding variance ----
axs[1, 0].plot(t_var, omega_var)
axs[1, 0].set_xlabel("Time")
axs[1, 0].set_ylabel("Var(Ω)")
axs[1, 0].set_title("Sliding-Window Variance of Ω")

# ---- Coarse-graining ----
axs[1, 1].plot(scales, omega_scale, marker="o")
axs[1, 1].set_xscale("log", base=2)
axs[1, 1].set_xlabel("Coarse-graining scale")
axs[1, 1].set_ylabel("Mean Ω")
axs[1, 1].set_title("Ω under Coarse-Graining")

plt.tight_layout()
plt.show()
