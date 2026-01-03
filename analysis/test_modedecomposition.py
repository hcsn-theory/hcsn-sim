# analysis/test_omega_modes.py
import json
import numpy as np

with open("analysis/omega_timeseries.json") as f:
    data = json.load(f)

omega = np.array([d["omega"] for d in data])
omega -= omega.mean()

fft = np.abs(np.fft.rfft(omega))
freq = np.fft.rfftfreq(len(omega))

# Find dominant modes
idx = np.argsort(fft)[-5:]

print("Dominant Ω modes:")
for i in idx:
    print(f"freq={freq[i]:.4f}, amplitude={fft[i]:.4f}")