import json
import matplotlib.pyplot as plt

WINDOW = 50

def defect_support(defect_time, rewrite_history, window=WINDOW):
    support = set()
    for r in rewrite_history:
        if abs(r["time"] - defect_time) <= window:
            support |= set(r["rewrite"].get("added_vertices", []))
            support |= set(r["rewrite"].get("removed_vertices", []))
    return support

def main():
    with open("timeseries.json") as f:
        data = json.load(f)

    run = data["runs"][-1]
    defects = run["defects"]
    history = run["rewrite_history"]

    dt_vals = []
    influence_vals = []

    for i, d1 in enumerate(defects):
        for d2 in defects[i+1:]:
            dt = d2["time"] - d1["time"]
            if dt <= 0:
                continue

            s1 = defect_support(d1["time"], history)
            s2 = defect_support(d2["time"], history)

            influenced = 1 if (s1 & s2) else 0

            dt_vals.append(dt)
            influence_vals.append(influenced)

    plt.scatter(dt_vals, influence_vals, s=10, alpha=0.6)
    plt.xlabel("Δt (rewrite steps)")
    plt.ylabel("Influence detected (1=yes, 0=no)")
    plt.title("Emergent Causal Cone (HCSN)")
    plt.show()

if __name__ == "__main__":
    main()