# analysis/detect_proto_particles.py

import json
import sys
from collections import defaultdict

# -----------------------------
# Detection thresholds
# -----------------------------
MIN_LIFETIME = 20
MIN_MEAN_SIZE = 10


# ============================================================
# CORE FUNCTION (IMPORT-SAFE)
# ============================================================
def detect_clusters(rewrites):
    """
    Detect and track proto-particles (ξ-clusters) by cluster ID.

    Returns:
        dict with statistics and per-cluster data
    """

    cluster_birth = {}
    cluster_last_seen = {}
    cluster_sizes = defaultdict(list)

    # -----------------------------
    # Track clusters over time
    # -----------------------------
    for r in rewrites:
        t = r["time"]
        sizes = r.get("cluster_sizes", {})

        for cid, size in sizes.items():
            if size <= 0:
                continue

            if cid not in cluster_birth:
                cluster_birth[cid] = t

            cluster_last_seen[cid] = t
            cluster_sizes[cid].append(size)

    # -----------------------------
    # Compute statistics
    # -----------------------------
    lifetimes = {}
    mean_sizes = {}

    for cid in cluster_birth:
        lifetime = cluster_last_seen[cid] - cluster_birth[cid]
        if lifetime <= 0:
            continue

        lifetimes[cid] = lifetime
        mean_sizes[cid] = sum(cluster_sizes[cid]) / len(cluster_sizes[cid])

    # -----------------------------
    # Global stats
    # -----------------------------
    valid_clusters = [
        cid for cid in lifetimes
        if lifetimes[cid] >= MIN_LIFETIME
        and mean_sizes[cid] >= MIN_MEAN_SIZE
    ]

    stats = {
        "num_clusters": len(valid_clusters),
        "lifetimes": lifetimes,
        "mean_sizes": mean_sizes,
        "valid_clusters": valid_clusters,
        "mean_lifetime": (
            sum(lifetimes[cid] for cid in valid_clusters) / len(valid_clusters)
            if valid_clusters else 0.0
        ),
        "max_lifetime": (
            max(lifetimes[cid] for cid in valid_clusters)
            if valid_clusters else 0
        ),
        "mean_cluster_size": (
            sum(mean_sizes[cid] for cid in valid_clusters) / len(valid_clusters)
            if valid_clusters else 0.0
        ),
    }

    return stats


# ============================================================
# CLI ENTRY POINT
# ============================================================
def main():
    if len(sys.argv) < 2:
        print("Usage: python3 -m analysis.detect_proto_particles <json_file>")
        sys.exit(1)

    path = sys.argv[1]
    with open(path) as f:
        data = json.load(f)

    rewrites = data.get("rewrite_history", [])

    stats = detect_clusters(rewrites)

    # -----------------------------
    # Report
    # -----------------------------
    print("\n=== Proto-Particle Detection ===")
    print(f"Total proto-objects     : {stats['num_clusters']}")
    print(f"Mean lifetime           : {stats['mean_lifetime']:.2f}")
    print(f"Max lifetime            : {stats['max_lifetime']}")
    print(f"Mean ξ-cluster size     : {stats['mean_cluster_size']:.2f}")

    if stats["num_clusters"] > 0:
        print("✅ Proto-particles detected")
    elif stats["mean_lifetime"] >= 5:
        print("⚠ Marginal proto-objects")
    else:
        print("❌ No proto-particles (noise)")


# ============================================================
# SAFE EXECUTION
# ============================================================
if __name__ == "__main__":
    main()