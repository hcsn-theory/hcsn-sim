# analysis/interaction_strength.py

import json
import numpy as np

def main():
    with open("analysis/particles.json") as f:
        particles = json.load(f)

    with open("analysis/defect_momentum_timeseries.json") as f:
        defect_stats = json.load(f)

    var_p_by_time = {
        d["time"]: d["var_p"]
        for d in defect_stats
        if d["var_p"] > 0
    }

    particle_data = []

    for p in particles:
        vars_p = []
        for t in p["times"]:
            if t in var_p_by_time:
                vars_p.append(var_p_by_time[t])

        if not vars_p:
            continue

        mass = 1.0 / np.mean(vars_p)
        mean_time = np.mean(p["times"])

        particle_data.append({
            "id": p["particle_id"],
            "mass": mass,
            "time": mean_time
        })

    interactions = []

    for i in range(len(particle_data)):
        for j in range(i + 1, len(particle_data)):
            dt = abs(particle_data[i]["time"] - particle_data[j]["time"])
            if dt == 0:
                continue

            dm = abs(particle_data[i]["mass"] - particle_data[j]["mass"])
            g = dm / dt
            interactions.append(g)

    if not interactions:
        print("No interactions measured.")
        return

    print("\n=== Interaction Strength Statistics ===")
    print(f"Samples: {len(interactions)}")
    print(f"Mean g: {np.mean(interactions):.3e}")
    print(f"Std g:  {np.std(interactions):.3e}")
    print(f"Max g:  {np.max(interactions):.3e}")

if __name__ == "__main__":
    main()