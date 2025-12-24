# analysis/defects.py

import numpy as np

def defect_momentum(defects, defect, window=20):
    """
    Purely observational momentum:
    imbalance of defect events around this defect.
    """
    t0 = defect["time"]

    before = 0
    after = 0

    for d in defects:
        dt = d["time"] - t0
        if abs(dt) > window or dt == 0:
            continue
        if dt < 0:
            before += 1
        else:
            after += 1

    return after - before


def defect_acceleration(momentum):
    """
    Discrete acceleration from momentum series.
    """
    return np.diff(momentum)

def defect_momentum_at_time(defects, center_time, window=20):
    """
    Momentum measured at an arbitrary observation time.
    """
    before = 0
    after = 0

    for d in defects:
        dt = d["time"] - center_time
        if abs(dt) > window or dt == 0:
            continue
        if dt < 0:
            before += 1
        else:
            after += 1

    return after - before

def momentum_timeseries(defects, defect, window=20, step=5):
    """
    Returns (times, momenta) for one defect.
    """
    t0 = defect["time"]

    # estimate lifetime from neighboring defects
    times = [d["time"] for d in defects]
    idx = times.index(t0)

    t_start = times[idx - 1] if idx > 0 else t0
    t_end   = times[idx + 1] if idx < len(times) - 1 else t0

    ts = []
    ps = []

    for t in range(t_start, t_end + 1, step):
        p = defect_momentum_at_time(defects, t, window)
        ts.append(t)
        ps.append(p)

    return ts, ps