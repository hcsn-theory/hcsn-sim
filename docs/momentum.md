# Step 11 — Formal Definition of Momentum in HCSN

## 11.1 Motivation

In **HCSN (Hierarchical Causal Structure Network)** there is:

- no background space
- no predefined geometry
- no notion of velocity

Therefore, momentum **cannot** be defined as \( p = mv \).

Instead, momentum must be an **intrinsic, operational quantity** that measures how a defect propagates through *causal structure* and how strongly it resists redirection by network rewrites.

---

## 11.2 Primitive Objects

The theory already defines the following primitives:

- Discrete time parameter \( t \)
- A causal structure \( \mathcal{C} \)
- Topological defects detected via label violation \( \Delta Q \)
- For each defect \( i \), a sequence of causal positions:

\[
C_i(t_1), C_i(t_2), \dots, C_i(t_n)
\]

Here, \( C_i(t) \) is **causal depth**, not spatial position.

---

## 11.3 Causal Displacement

Define the **causal displacement per step** for defect \( i \):

\[
\Delta C_i(k) = C_i(t_{k+1}) - C_i(t_k)
\]

Properties:

- Discrete
- Dimensionless
- Purely relational
- Independent of any embedding space

---

## 11.4 Definition of Momentum

### Formal Definition

> **Momentum (HCSN):**  
The momentum of a defect is defined as the square root of the variance of its causal displacement.

\[
\boxed{
p_i
\;=\;
\sqrt{
\operatorname{Var}\!\left(\Delta C_i\right)
}
}
\]

Expanded form:

\[
p_i
=
\sqrt{
\frac{1}{N}
\sum_{k=1}^{N}
\left(
\Delta C_i(k)
-
\langle \Delta C_i \rangle
\right)^2
}
\]

with

\[
\langle \Delta C_i \rangle
=
\frac{1}{N}
\sum_{k=1}^{N}
\Delta C_i(k)
\]

---

## 11.5 Physical Interpretation

This definition satisfies the **functional role of momentum**:

### Directional persistence
- Low variance → straight, stable causal propagation
- High variance → scattering, zig-zagging, interaction-heavy propagation

### Interaction sensitivity
- Each causal interaction contributes to variance
- Momentum accumulates statistically

### Observer independence
- No reference frame required
- No coordinate system assumed

Momentum is intrinsic to the defect, not the observer.

---

## 11.6 What Momentum Is *Not* in HCSN

This definition does **not** assume:

- Mass
- Spatial distance
- Metric tensor
- Speed of light
- Hamiltonian or Lagrangian structure

Momentum is **emergent**, not postulated.

---

## 11.7 Relation to Energy (Deferred)

Energy will be defined later via:

- defect lifetime
- acceptance suppression
- causal interaction cost

Dispersion relations \( E(p) \) are therefore **measured**, not assumed.

---

## 11.8 Computational Correspondence

In simulation code, momentum corresponds to:

```python
var_p = np.var(causal_displacements)
p = np.sqrt(var_p)
