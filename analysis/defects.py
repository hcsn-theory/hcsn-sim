# analysis/defects.py

def defect_support_vertices(engine):
    """
    Vertices touched by the rewrite that triggered the defect.
    """
    if engine.last_rewrite is None:
        return set()

    return set(
        engine.last_rewrite.get("added_vertices", [])
        + engine.last_rewrite.get("removed_vertices", [])
    )


def defect_momentum(engine, defect_event, window=20):
    """
    Observational momentum: rewrite-flow asymmetry
    around a defect event.
    """
    t0 = defect_event["time"]
    support = defect_support_vertices(engine)

    before = 0
    after = 0

    for r in engine.rewrite_history:
        if abs(r["time"] - t0) > window:
            continue

        touched = set(r["rewrite"]["added_vertices"]) & support
        if not touched:
            continue

        if r["time"] < t0:
            before += 1
        else:
            after += 1

    return after - before

def defect_acceleration(momentum_series):
    """
    Discrete acceleration from momentum history.
    """
    return [
        momentum_series[i+1] - momentum_series[i]
        for i in range(len(momentum_series) - 1)
    ]