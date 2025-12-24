# analysis/track_particles.py

import json
import numpy as np
from collections import defaultdict

# -----------------------------
# Parameters (observational)
# -----------------------------
PERSISTENCE_THRESHOLD = 0.6   # particle identity criterion
WINDOW = 40                   # rewrite-time window for support


# -----------------------------
# Defect support (purely empirical)
# -----------------------------
def defect_support(defect_time, rewrite_history, window=WINDOW):
    support = set()
    for r in rewrite_history:
        if abs(r["time"] - defect_time) <= window:
            support |= set(r["rewrite"].get("added_vertices", []))
            support |= set(r["rewrite"].get("removed_vertices", []))
    return support


def persistence(s1, s2):
    if not s1 or not s2:
        return 0.0
    return len(s1 & s2) / len(s1 | s2)


# -----------------------------
# Main particle tracking
# -----------------------------
def main():
    with open("timeseries.json") as f:
        data = json.load(f)

    runs = data["runs"]
    run = runs[-1]

    defects = run.get("defects", [])
    rewrite_history = run.get("rewrite_history", [])

    if len(defects) < 2 or not rewrite_history:
        print("Not enough data to track particles.")
        return

    # Precompute supports
    supports = [
        defect_support(d["time"], rewrite_history)
        for d in defects
    ]

    # Particle tracks: list of lists of defect indices
    particles = []

    for i, d in enumerate(defects):
        placed = False

        for track in particles:
            j = track[-1]
            p = persistence(supports[i], supports[j])

            if p >= PERSISTENCE_THRESHOLD:
                track.append(i)
                placed = True
                break

        if not placed:
            particles.append([i])

    # -----------------------------
    # Report particle properties
    # -----------------------------
    print("\n=== Particle Tracking Results ===\n")
    print(f"Total defects:   {len(defects)}")
    print(f"Total particles:{len(particles)}\n")

    for pid, track in enumerate(particles):
        times = [defects[i]["time"] for i in track]
        omegas = [defects[i]["omega"] for i in track]

        lifetime = max(times) - min(times)
        mean_omega = np.mean(omegas)

        print(f"Particle {pid}:")
        print(f"  Defects:  {len(track)}")
        print(f"  Lifetime: {lifetime}")
        print(f"  Mean Ω:   {mean_omega:.3f}")
        print(f"  Times:    {times}")
        print()

    # -----------------------------
    # Save particle tracks
    # -----------------------------
    particle_data = []

    for pid, track in enumerate(particles):
        particle_data.append({
            "particle_id": pid,
            "defects": track,
            "times": [defects[i]["time"] for i in track],
            "omegas": [defects[i]["omega"] for i in track],
        })

    with open("analysis/particles.json", "w") as f:
        json.dump(particle_data, f, indent=2)

    print("Saved particle tracks to analysis/particles.json")


if __name__ == "__main__":
    main()