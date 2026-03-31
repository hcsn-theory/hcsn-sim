import os

# ============================================================
# Physics parameters (externally controlled, engine-safe)
# ============================================================

GAMMA_DEFECT = float(os.getenv("HCSN_GAMMA_DEFECT", 0.15))
INERTIA_SCALE = float(os.getenv("HCSN_INERTIA_SCALE", 1.0))
INTERACTION_BOOST = float(os.getenv("HCSN_INTERACTION_BOOST", 1.02))


class PhysicsParams:
    def __init__(self):
        self.gamma_defect = GAMMA_DEFECT
        self.inertia_scale = INERTIA_SCALE
        self.interaction_boost = INTERACTION_BOOST
        self.noise_bias = 0.0
        self.defect_injection = 0.0
        self.geometry_freeze = 0.9
