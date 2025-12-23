# Worldlines and Persistence in HCSN

## Status
**Derived from simulation behavior**  
No additional axioms beyond HCSN rewrite dynamics are assumed.

---

## 1. Motivation

Having identified **defects** as discrete, localized failures of hierarchical closure, the next question is unavoidable:

> How do defects *persist* through time?

In HCSN, there is no background spacetime and no predefined notion of trajectory.  
Worldlines must therefore **emerge**, not be imposed.

This document formalizes how persistence arises naturally from rewrite dynamics.

---

## 2. Temporal Structure Without Time

### Definition 2.1 — Causal Time

In HCSN, **time** is identified with:
- rewrite step count,
- causal chain depth,
- ordering induced by rewrite application.

There is no external clock — only relational succession.

---

## 3. Defect Persistence

### Definition 3.1 — Persistent Defect

A defect is **persistent** if:
- multiple defect events occur within a bounded time window,
- each event occurs in a locally correlated hypergraph region,
- defect charge varies continuously (no abrupt disappearance).

Formally, a sequence \( \{t_i\} \) is persistent if:
\[
\max(t_{i+1} - t_i) < \tau_{\text{max}}
\]

for some finite threshold \( \tau_{\text{max}} \).

---

## 4. Worldlines as Equivalence Classes

### Definition 4.1 — Defect Worldline

A **worldline** is an equivalence class of defect events satisfying:
- temporal proximity,
- local geometric continuity,
- approximate charge conservation.

Worldlines are **not paths in space** —  
they are **chains of causally related instabilities**.

---

## 5. Emergent Motion

### Observational Law 5.1 — Motion Without Coordinates

Simulation data shows that:
- defects reappear in successive rewrite steps,
- their local neighborhood shifts under rewrites,
- no defect remains fixed relative to the entire hypergraph.

This gives rise to an effective notion of **motion**:
- motion is the *migration of instability*,
- not displacement in a coordinate system.

---

## 6. Velocity as Rewrite Rate

### Definition 6.1 — Effective Velocity

Define effective velocity \( v \) as:
\[
v \sim \frac{\Delta \text{support}}{\Delta t}
\]

where:
- support is the number of hyperedges affected by the defect,
- \( \Delta t \) is rewrite time.

**Observation:**  
High-rewrite-density regions correlate with faster defect propagation.

---

## 7. Stability and Mass Analogy

### Observational Law 7.1 — Persistence–Stability Relation

Defects with:
- smaller charge fluctuations,
- lower local rewrite entropy,

persist longer and propagate more slowly.

This suggests an emergent **mass-like behavior**:
- persistence ↔ inertia,
- instability ↔ mobility.

This is an analogy, not an assumption.

---

## 8. Worldline Termination

### Definition 8.1 — Annihilation

A worldline terminates when:
- defect charge returns to zero,
- no correlated defect appears within \( \tau_{\text{max}} \).

Simulation data shows:
- annihilation often occurs in pairs,
- frequently near regions of geometric reorganization.

---

## 9. Interaction of Worldlines

### Observational Law 9.1 — Worldline Interaction

When two worldlines approach:
- defect spacing decreases,
- charge variance increases,
- annihilation or deflection may occur.

No force law is imposed —  
interactions emerge from rewrite competition.

---

## 10. Coarse-Graining Consistency

### Observational Law 10.1 — Scale Covariance

Under coarse-graining:
- individual defect events blur,
- worldlines remain identifiable,
- long-lived structures persist.

Worldlines are therefore **scale-stable features**.

---

## 11. Interpretation

Worldlines in HCSN are:
- records of sustained topological instability,
- causal structures, not geometric objects,
- emergent carriers of information.

They precede particles, trajectories, and spacetime.

---

## 12. Conjectures (Explicit)

> **Conjecture 12.1**  
Long-lived defect worldlines correspond to particle states.

> **Conjecture 12.2**  
Worldline interactions encode scattering amplitudes.

These are not assumed and remain testable.

---

## 13. Next Steps

The following developments are now logically enabled:

1. Classification of worldlines by persistence
2. Emergent momentum and energy definitions
3. Interaction graphs between worldlines
4. Backreaction of worldlines on geometry

No new axioms are required.

---

## 14. Summary

- Worldlines emerge from persistence, not coordinates.
- Motion is rewrite-driven, not spatial.
- Stability gives rise to mass-like behavior.
- Interactions arise without forces.

HCSN does not place objects in spacetime —  
**it makes spacetime remember them.**
