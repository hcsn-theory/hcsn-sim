# Dimension and Geometry Selection in HCSN

## Motivation

In HCSN, there is no background space, lattice, or manifold.
Geometry must therefore emerge dynamically from rewrite statistics.

A natural candidate for emergent dimension is the average coordination number ⟨k⟩.
However, simulations show that ⟨k⟩ continues to grow slowly with time, even after
hierarchical stability (Ω) has saturated.

This document explains why this behavior is expected and how geometry should be
defined operationally rather than microscopically.

---

## Microscopic vs Effective Dimension

The raw coordination ⟨k⟩ measures local connectivity.
However:

- High ⟨k⟩ does not necessarily imply higher spatial dimension
- Many rewrites increase local redundancy without expanding causal reach
- Entropy favors higher-degree graphs

Therefore, ⟨k⟩ is not itself a physical observable.

Instead, **dimension must be defined after coarse-graining**.

---

## Coarse-Grained Geometry

Let G be the interaction graph derived from worldlines.
Define a coarse-graining operator C_ℓ acting at scale ℓ.

We define the effective dimension as: d_eff(ℓ) = f(⟨k⟩_ℓ, Ω_ℓ, Ψ_ℓ)

where:
- ⟨k⟩_ℓ is coordination after ℓ-scale coarse-graining
- Ω_ℓ is hierarchical closure stability
- Ψ_ℓ is redundancy density

Simulations indicate that while ⟨k⟩ grows microscopically,
d_eff stabilizes at finite scale.

---

## Interpretation

This behavior mirrors renormalization in quantum field theory:

- Microscopic degrees of freedom proliferate
- Macroscopic observables remain finite
- Geometry is an emergent fixed point

Thus, HCSN predicts **dimensional stability without dimensional rigidity**.

---

## Consequences

1. Dimension is not fundamental
2. High-degree connectivity may correspond to internal structure
3. Spatial geometry emerges only after coarse-graining

This framework allows internal degrees of freedom to arise naturally,
without invoking extra dimensions or Hilbert spaces.