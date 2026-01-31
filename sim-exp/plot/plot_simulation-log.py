import re
import matplotlib.pyplot as plt

LOG_FILE = "simulation.log"

# -----------------------------
# Read full log
# -----------------------------
with open(LOG_FILE, "r") as f:
    lines = f.readlines()

# -----------------------------
# Find last run
# -----------------------------
run_start_indices = [
    i for i, line in enumerate(lines)
    if "RUN STARTED:" in line
]

if not run_start_indices:
    raise RuntimeError("No RUN STARTED marker found in simulation.log")

start_idx = run_start_indices[-1]
run_lines = lines[start_idx:]

# -----------------------------
# Storage
# -----------------------------
t = []
k = []
phi = []
psi = []
omega = []
acc = []
defect_times = []

# -----------------------------
# Parse only last run
# -----------------------------
for line in run_lines:
    line = line.strip()

    # Defect events
    if line.startswith("*** DEFECT EVENT"):
        m = re.search(r"t=(\d+)", line)
        if m:
            defect_times.append(int(m.group(1)))
        continue

    # Skip headers
    if (
        not line
        or line.startswith("=")
        or line.startswith("RUN STARTED")
        or line.startswith("time |")
    ):
        continue

    if "|" in line:
        parts = [p.strip() for p in line.split("|")]

        # We require omega column explicitly
        if len(parts) < 10:
            continue

        try:
            t_val = int(parts[0])
            k_val = float(parts[2])
            phi_val = float(parts[6])
            psi_val = float(parts[7])
            acc_val = float(parts[8].replace("%", ""))
            omega_val = float(parts[9])

        except ValueError:
            continue

        # Append ONLY if everything parsed
        t.append(t_val)
        k.append(k_val)
        phi.append(phi_val)
        psi.append(psi_val)
        acc.append(acc_val)
        omega.append(omega_val)

# --- checker --

print("Parsed points:", len(t), len(omega))

if not t or not omega:
    raise RuntimeError("No valid data parsed from simulation.log")


# -- graph --

plt.figure(figsize=(12, 6))

plt.plot(t, omega, label="Ω(t)")
plt.plot(t, k, label="⟨k⟩(t)", linestyle="--")

for i, td in enumerate(defect_times):
    plt.axvline(td, color="red", alpha=0.3,
                label="defect" if i == 0 else None)

plt.xlabel("Time")
plt.ylabel("Value")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()
