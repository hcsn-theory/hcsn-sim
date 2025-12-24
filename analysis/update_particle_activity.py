def update_particle_activity(engine, particle_tracks):
    touched = engine.touched_vertices()

    for p in particle_tracks:
        # particle support = union of defect supports
        support = set(p["times"])  # or vertex support if you track that

        if touched & support:
            pid = p["particle_id"]
            engine.particle_activity[pid] = (
                engine.particle_activity.get(pid, 0) + 1
            )