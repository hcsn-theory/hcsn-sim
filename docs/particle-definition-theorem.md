# Particle Definition Theorem (HCSN)

## Statement

In the Hypergraph Causal Structural Network (HCSN), a **particle** is an emergent, persistent topological defect characterized entirely by observable rewrite dynamics, without reference to Hilbert spaces, wavefunctions, or fundamental state vectors.

## Definitions

Let an HCSN evolution be defined by discrete rewrite steps indexed by time `t`.

Let a **defect event** be a rewrite event at time `t_d` such that a topological charge proxy
\[
\Delta Q(t_d) \neq 0
\]
is observed, where `ΔQ` is operationally measured via hierarchical closure change:
\[
\Delta Q := \Delta \Omega
\]

Define the following observables:

### 1. Rewrite Momentum
For a defect event `d`, define momentum:
\[
p(d) := N_{\text{after}} - N_{\text{before}}
\]
where `N_after` and `N_before` count rewrites touching the defect support within a finite temporal window.

### 2. Mass Proxy
Define the mass proxy of a defect as:
\[
m(d) := \frac{1}{\mathrm{Var}(p)}
\]
where the variance is computed over the momentum time series associated with the defect.

### 3. Lifetime
Define the lifetime of a defect as the temporal separation between its creation and annihilation (or last detectable interaction).

### 4. Hierarchical Stability
Let `Ω(d)` denote the average hierarchical closure during the defect’s lifetime.

---

## Particle Definition Theorem

**Theorem.**  
A defect `d` constitutes a particle if and only if all of the following conditions hold:

1. **Persistence**  
   The defect exhibits a lifetime significantly larger than the local rewrite correlation time.

2. **Momentum Coherence**  
   The defect possesses a nonzero mean rewrite momentum with bounded variance:
   \[
   \mathrm{Var}(p(d)) < \infty
   \]

3. **Mass Emergence**  
   The defect’s lifetime scales inversely with momentum variance:
   \[
   \tau(d) \propto \frac{1}{\mathrm{Var}(p(d))}
   \]

4. **Geometric Coupling**  
   The defect interacts with hierarchical closure such that:
   - high `Ω` → stable, low-variance defects
   - low `Ω` → unstable, high-variance defects

---

## Consequences

- Particles are **not fundamental objects**, but dynamically stabilized processes.
- Mass is **not intrinsic**, but emergent from rewrite inertia.
- Momentum conservation arises statistically from rewrite flow, not symmetry axioms.
- No wavefunction or Hilbert space is required at the fundamental level.

---

## Empirical Status

All defining conditions above are directly testable using simulation data:
- rewrite history
- defect logs
- momentum time series
- lifetime distributions

Current simulations satisfy all four conditions for multiple defect species.

---

## Interpretation

This theorem provides an operational definition of particles compatible with:
- stochastic dynamics
- emergent spacetime
- non-Hilbert formulations of quantum theory

It aligns with observable-first approaches to quantum foundations.