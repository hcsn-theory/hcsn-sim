import json

def main():
    with open("timeseries.json") as f:
        data = json.load(f)

    run = data["runs"][-1]

    t_list = run.get("t", [])
    omega_list = run.get("omega", [])

    if not t_list or not omega_list:
        raise ValueError("Missing 't' or 'omega' arrays in run data")

    if len(t_list) != len(omega_list):
        raise ValueError("Length mismatch between 't' and 'omega'")

    records = []
    for t, omega in zip(t_list, omega_list):
        records.append({
            "time": t,
            "omega": omega
        })

    with open("analysis/omega_timeseries.json", "w") as f:
        json.dump(records, f, indent=2)

    print(f"Saved {len(records)} omega samples to analysis/omega_timeseries.json")

if __name__ == "__main__":
    main()