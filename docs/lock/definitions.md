# Core Definitions and Mathematical Objects

## Hypergraph

A hypergraph is defined as:
\[
H = (V, E)
\]
where \( V \) is a set of vertices and \( E \subseteq \mathcal{P}(V) \) is a set of hyperedges.

---

## Rewrite Rules

A rewrite rule \( \mathcal{R} \) is a mapping:
\[
\mathcal{R} : H \rightarrow H'
\]
acting on a bounded induced subgraph.

---

## Causal Graph

The causal graph \( \mathcal{C}(H) \) is the DAG formed by rewrite dependencies.
Nodes represent rewrites; edges represent causal necessity.

---

## Interaction Graph

The interaction graph is a projection of rewrite overlap,
encoding which worldlines interact across rewrites.

---

## Hierarchical Closure Ω

Ω is a scalar functional measuring hierarchical closure across causal scales:

\[
\Omega = \mathcal{F}(\text{interaction graph}, \text{rewrite depth})
\]

Ω is dimensionless and dynamically evolving.

---

## Defects

A defect is a persistent violation of local closure constraints.
Defects exhibit worldline-like behavior under repeated rewrites.