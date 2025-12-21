import json
import matplotlib.pyplot as plt

# -----------------------------
# Load time series data
# -----------------------------
with open("timeseries.json", "r") as f:
    data = json.load(f)

t = data["t"]                  # time steps
k = data["k"]                  # <k>(t)
omega = data["omega"]          # Ω(t)
defects = data["defects"]      # defect events

defect_times = [d["time"] for d in defects]

# -----------------------------
# Plot
# -----------------------------
plt.figure(figsize=(11, 6))

# Ω(t)
plt.plot(
    t, omega,
    label="Ω(t)  (hierarchical closure)",
    linewidth=2
)

# <k>(t)
plt.plot(
    t, k,
    label="⟨k⟩(t)  (average coordination)",
    linewidth=2
)

# Defect markers
for i, td in enumerate(defect_times):
    plt.axvline(
        x=td,
        color="red",
        linestyle="--",
        alpha=0.5,
        label="topological defect" if i == 0 else None
    )

# -----------------------------
# Formatting
# -----------------------------
plt.xlabel("Time (rewrite steps)")
plt.ylabel("Value")
plt.title("Emergent Geometry, Topology, and Defect Events")

plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

plt.show()