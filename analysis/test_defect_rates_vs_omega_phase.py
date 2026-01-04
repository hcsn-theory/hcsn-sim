import json
import numpy as np

with open("timeseries.json") as f:
    data = json.load(f)

run = data["runs"][-1]
times = np.array(run["t"])
omegas = np.array(run["omega"])
defects = run["defects"]

birth_omegas = []

for d in defects:
    t = d["time"]
    idx = np.argmin(np.abs(times - t))
    birth_omegas.append(omegas[idx])

print("Defects:", len(birth_omegas))
print(f"Mean Ω at defect birth ≈ {np.mean(birth_omegas):.3f}")
print(f"Std  Ω at defect birth ≈ {np.std(birth_omegas):.3f}")