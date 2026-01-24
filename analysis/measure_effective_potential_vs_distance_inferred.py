import json
import sys
import math
from collections import defaultdict, deque


def is_finite(x):
    return isinstance(x, (int, float)) and math.isfinite(x)


def bfs_cluster_distance(inter, cluster_A, cluster_B, max_depth=50):
    visited = set(cluster_A)
    queue = deque((v, 0) for v in cluster_A)

    while queue:
        v, d = queue.popleft()
        if d > max_depth:
            break
        if v in cluster_B:
            return d
        for u in inter.get(v, []):
            if u not in visited:
                visited.add(u)
                queue.append((u, d + 1))

    return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 -m analysis.measure_effective_potential_vs_distance_inferred <json>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = json.load(f)

    interaction_log = data.get("interaction_log", [])
    if not interaction_log:
        print("❌ No interaction_log")
        return

    bins = defaultdict(list)
    prev_activity = {}

    for entry in interaction_log:
        xi_clusters = entry.get("xi_clusters", {})
        xi_support = entry.get("xi_support", {})

        if not xi_clusters or not xi_support:
            continue

        # Build cluster → vertices
        clusters = {}
        for v, cid in xi_clusters.items():
            clusters.setdefault(cid, set()).add(int(v))

        if len(clusters) < 2:
            continue

        # Approximate interaction graph
        inter = {}
        for v in xi_support.keys():
            inter.setdefault(int(v), set())

        activity = sum(v for v in xi_support.values() if is_finite(v))

        cids = list(clusters.keys())[:2]
        d = bfs_cluster_distance(inter, clusters[cids[0]], clusters[cids[1]])

        if d is None:
            continue

        prev = prev_activity.get(d)
        if prev is not None:
            delta_phi = prev - activity
            if is_finite(delta_phi):
                bins[d].append(delta_phi)

        prev_activity[d] = activity

    if not bins:
        print("❌ No inferred distance samples")
        return

    print("\n=== D2 (INFERRED) — Effective Potential vs Distance ===\n")

    for d in sorted(bins):
        vals = bins[d]
        mean = sum(vals) / len(vals)
        var = sum((x - mean) ** 2 for x in vals) / len(vals)
        print(
            f"d = {d:3d} | "
            f"samples = {len(vals):4d} | "
            f"⟨ΔΦ⟩ = {mean:.6e} | "
            f"Var = {var:.6e}"
        )

    print("\n⚠ Inferred diagnostic complete (non-authoritative)")


if __name__ == "__main__":
    main()