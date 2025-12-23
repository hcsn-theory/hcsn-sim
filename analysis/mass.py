# analysis/mass.py
import statistics

def mass_proxy(momentum_series, eps=1e-6):
    """
    Emergent inertial mass proxy.
    """
    if len(momentum_series) < 2:
        return float("inf")

    var = statistics.pvariance(momentum_series)
    return 1.0 / (var + eps)