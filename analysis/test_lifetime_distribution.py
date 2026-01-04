import numpy as np
from scipy.stats import expon, lognorm

lifetimes = np.load("analysis/lifetimes.npy")

# Fit exponential
loc_e, scale_e = expon.fit(lifetimes, floc=0)

# Fit lognormal
shape_l, loc_l, scale_l = lognorm.fit(lifetimes, floc=0)

print("=== Lifetime Distribution Fits ===")
print(f"Exponential scale ≈ {scale_e:.2f}")
print(f"Lognormal shape  ≈ {shape_l:.2f}")