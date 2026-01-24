import json
import sys
import math


def finite(x):
    return isinstance(x, (int, float)) and math.isfinite(x)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 -m analysis.measure_environment_conservation <json>")
        sys.exit(1)

    path = sys.argv[1]
    with open(path) as f:
        data = json.load(f)

    interaction_log = data.get("interaction_log", [])
    if not interaction_log:
        print("❌ No interaction_log found")
        return

    # -----------------------------
    # Finite ξ_total at endpoints
    # -----------------------------
    def finite_xi_total(entry):
        xi_support = entry.get("xi_support", {})
        return sum(v for v in xi_support.values() if finite(v))

    xi_start = finite_xi_total(interaction_log[0])
    xi_end   = finite_xi_total(interaction_log[-1])
    dxi_total = xi_end - xi_start

    # -----------------------------
    # Cluster ξ evolution (finite)
    # -----------------------------
    cluster_birth = {}
    cluster_last = {}

    for entry in interaction_log:
        clusters = entry.get("xi_clusters", {})
        support = entry.get("xi_support", {})

        for v, cid in clusters.items():
            val = support.get(v, 0.0)
            if not finite(val):
                continue

            if cid not in cluster_birth:
                cluster_birth[cid] = 0.0
            cluster_birth[cid] += val

            cluster_last[cid] = cluster_last.get(cid, 0.0) + val

    if len(cluster_birth) < 2:
        print("❌ Need ≥2 clusters for C7")
        return

    cids = sorted(cluster_birth.keys())[:2]
    A, B = cids

    dxi_A = cluster_last[A] - cluster_birth[A]
    dxi_B = cluster_last[B] - cluster_birth[B]
    dxi_clusters = dxi_A + dxi_B

    # -----------------------------
    # Environment = remainder
    # -----------------------------
    dxi_env = dxi_total - dxi_clusters

    residual = abs(dxi_total - (dxi_clusters + dxi_env))
    norm = abs(dxi_total) + abs(dxi_clusters) + abs(dxi_env)

    epsilon = residual / norm if norm > 0 else 0.0

    # -----------------------------
    # Output
    # -----------------------------
    print("\n=== Environment Conservation Test (C7, finite ξ only) ===")
    print(f"Cluster A ID       : {A}")
    print(f"Cluster B ID       : {B}")
    print(f"Δξ_A (finite)      : {dxi_A}")
    print(f"Δξ_B (finite)      : {dxi_B}")
    print(f"Δξ_clusters        : {dxi_clusters}")
    print(f"Δξ_total (finite)  : {dxi_total}")
    print(f"Δξ_env             : {dxi_env}")
    print(f"Residual |ΣΔξ|     : {residual}")
    print(f"Normalized ε       : {epsilon:.6f}")

    if epsilon < 0.1:
        print("✅ Approximate conservation detected (finite sector)")
    else:
        print("❌ No conservation law observed")


if __name__ == "__main__":
    main()