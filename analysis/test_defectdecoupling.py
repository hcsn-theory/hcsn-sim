import json
import numpy as np

with open("analysis/omega_timeseries.json") as f:
    omega_data = json.load(f)

with open("timeseries.json") as f:
    run = json.load(f)["runs"][-1]

defect_times = set(d["time"] for d in run["defects"])

clean = [x for x in omega_data if x["time"] not in defect_times]

omega = np.array([x["omega"] for x in clean])

print("Ω variance away from defects:", omega.var())