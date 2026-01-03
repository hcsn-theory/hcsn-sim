import os

# ============================================================
# Physics parameters (externally controlled, engine-safe)
# ============================================================

GAMMA_DEFECT = float(os.getenv("HCSN_GAMMA_DEFECT", 0.15))
INERTIA_SCALE = float(os.getenv("HCSN_INERTIA_SCALE", 1.0))
INTERACTION_BOOST = float(os.getenv("HCSN_INTERACTION_BOOST", 1.02))