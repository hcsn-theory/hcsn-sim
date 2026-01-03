import json
import numpy as np

WINDOW = 5

def main():
    with open("analysis/particles.json") as f:
        particles = json.load(f)

    with open("analysis/omega_timeseries.json") as f:
        omega_series = json.load(f)

    times = np.array([o["time"] for o in omega_series])
    omegas = np.array([o["omega"] for o in omega_series])

    local_channels = []

    for pid, p in enumerate(particles):
        channel = []

        for t in p["times"]:
            # --- interpolate Ω at defect time ---
            if t < times[0] or t > times[-1]:
                continue

            omega_t = np.interp(t, times, omegas)

            idx = np.searchsorted(times, t)
            lo = max(0, idx - WINDOW)
            hi = min(len(omegas), idx + WINDOW)

            local_mean = omegas[lo:hi].mean()
            omega_local = omega_t - local_mean

            channel.append({
                "time": t,
                "omega_local": omega_local
            })

        if len(channel) >= 3:
            local_channels.append({
                "particle": pid,
                "channel": channel
            })

    with open("analysis/local_omega_channels.json", "w") as f:
        json.dump(local_channels, f, indent=2)

    print(f"Saved {len(local_channels)} local Ω channels")

if __name__ == "__main__":
    main()