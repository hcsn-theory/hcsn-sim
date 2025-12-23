import json
import matplotlib.pyplot as plt

# -----------------------------
# Load data
# -----------------------------
with open("timeseries.json", "r") as f:
    data = json.load(f)

latest_run = data["runs"][-1]

t = latest_run["t"]
k = latest_run["k"]
omega = latest_run["omega"]
defects = latest_run.get("defects", [])

defect_times = [d["time"] for d in defects]

# -----------------------------
# Plot
# -----------------------------
fig, ax1 = plt.subplots(figsize=(12, 6))

# Ω(t) on left axis
ax1.plot(
    t, omega,
    label="Ω(t) — hierarchical closure",
    linewidth=2
)
ax1.set_xlabel("Time (rewrite steps)")
ax1.set_ylabel("Ω")
ax1.tick_params(axis="y")

# <k>(t) on right axis
ax2 = ax1.twinx()
ax2.plot(
    t, k,
    linestyle="--",
    linewidth=2,
    label="⟨k⟩(t) — average coordination"
)
ax2.set_ylabel("⟨k⟩")
ax2.tick_params(axis="y")

# Defect markers
for i, td in enumerate(defect_times):
    ax1.axvline(
        x=td,
        color="red",
        linestyle=":",
        alpha=0.4,
        label="topological defect" if i == 0 else None
    )

# -----------------------------
# Legend & formatting
# -----------------------------
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()

ax1.legend(
    lines1 + lines2,
    labels1 + labels2,
    loc="upper left"
)

plt.title("Emergent Geometry and Topological Defects")
plt.grid(alpha=0.25)
plt.tight_layout()
plt.show()
