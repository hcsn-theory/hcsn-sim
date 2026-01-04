import json
import numpy as np

with open("analysis/signal_speed_samples.json") as f:
    samples = json.load(f)

speeds = [1.0 / s["dt"] for s in samples if s["influence"] == 1]

speeds = np.array(speeds)
vmax = speeds.max()

delta_v = np.std(speeds[speeds > 0.8 * vmax])

print("=== STEP 4: Lorentz Cone Sharpness ===")
print(f"v_max ≈ {vmax:.6f}")
print(f"Δv (cone width) ≈ {delta_v:.6f}")