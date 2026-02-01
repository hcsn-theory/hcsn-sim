# 🌀 HCSN Theory — Hierarchial Closure Structure Network


[![DOI](https://zenodo.org/badge/1118466950.svg)](https://doi.org/10.5281/zenodo.18025757)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0004--1698--5729-green.svg)](https://orcid.org/0009-0004-1698-5729)

---

> HCSN (Hierarchial Closure Structure Network) explores the hypothesis that the universe is fundamentally computational — discrete events and causal relations .

✨ Highlights
- Minimal, local rewrite rules drive evolution.
- Diagnostics test emergence of time, dimensionality, and metric structure.
- Designed as a research playground: toy universes, experiments, and visualization.

---

Table of Contents
- [Overview](#overview)
- [Repository Structure](#repository-structure)
- [Quick Start](#quick-start)
- [How to Run](#how-to-run-a-toy-universe)
- [Diagnostics Explained](#diagnostics-explained)
- [Current Research Focus](#current-research-focus)
- [Contributing](#contributing)
- [Acknowledgements & License](#acknowledgements)

---

## Overview

HCSN proposes a discrete, causal, and computational substrate:
- Events are vertices in a hypergraph; relations are (hyper)edges.
- Dynamics are local rewrite rules (edge creation, vertex fusion).
- Geometry, dimension, and time are emergent, not fundamental.

The long-term goal is to identify the minimal rule set that produces universes consistent with:
- Lorentz invariance (emergent)
- 4D spacetime structures
- Holographic scaling of information
- Quantum probabilistic behavior (Born rule)

---

## Repository Structure 

```text
HCSN-Theory/
├── engine/                # Core simulation engine
│   ├── hypergraph.py      # Vertices, hyperedges, causality
│   ├── rules.py           # Rewrite rules
│   ├── rewrite_engine.py  # Acceptance dynamics
│   └── observables.py     # Physical diagnostics
├── sim-exp/           # Reproducible experiments
├── figures/               # Generated plots & assets
├── analysis/
├── multiverse/
├── simulation.log
└── README.md
```

---

## Quick Start 

Requirements
- Python 3.10 or later
- No external dependencies by default (pure Python). If notebooks or plotting are used, consider: matplotlib, numpy, jupyter.

Clone and run:
```bash
git clone https://github.com/hcsn-theory/hcsn-sim.git
cd hcsn-sim
python3 -m analysis.interaction_experiment
```

This runs a universe and prints diagnostics every N steps (see config/flags in the engine if present).

---

## How to Run

1. Configure parameters (if available) in `engine` or via command-line flags.
2. Start the simulation:
   - `python3 -m analysis.interaction_experiment`
3. Key printed diagnostics (periodic):
   - average coordination ⟨k⟩
   - causal depth (L)
   - interaction concentration (Φ)
   - closure density (Ψ)
   - hierarchical stability (Ω)

---

## Diagnostics Explained 

| Symbol | Name | Meaning |
|:------:|------|--------|
| ⟨k⟩ | Avg coordination | Controls effective dimensionality; geometric attractor near 8. |
| L | Causal depth | Maximum causal chain length — emergent time scale. |
| Φ | Interaction concentration | Measures hub dominance (want small Φ for uniformity). |
| Ψ | Closure density | Redundancy in causal closure (error correction). |
| Ω | Hierarchical closure | RG-like stability across scales (non-zero indicates persistence). |

Interpretation guide:
- ⟨k⟩ ≈ 7.5–8.5 → spacetime-like, stable geometry.
- Small Φ → suppressed hubs, more uniform interactions.
- Non-zero Ω across scales → hierarchical persistence and robustness.

---

## Current Research Focus 

Active directions:
- Prevent metric collapse under coarse-graining
- Implement logarithmic information metrics (holographic tests)
- Enforce holographic bounds dynamically in evolution
- Search for Lorentz-invariant fixed points of the rule dynamics
- Explore mechanisms that produce quantum probabilistic outcomes (Born rule)

---

## Contributing

We welcome contributions from:
- physicists (GR, QFT, quantum gravity)
- mathematicians (graph theory, category theory)
- programmers (simulation performance, visualization)
- curious minds who can test assumptions

Getting started:
1. Fork the repo, create a feature branch.
2. Add reproducible experiments under `experiments/`.
3. Document new rules, diagnostics, and observed behaviors.
4. Open PRs with clear descriptions, expected behavior, and reproducibility notes.

Guidelines:
- Write reproducible code and seed RNGs where appropriate.
- Add tests or small example scripts demonstrating changes.
- Keep changes modular — new rules or observables should live in `engine/`.

---

## Acknowledgements

If you use HCSN-Theory in research, please cite the repo and include a reference to the simulation version/commit used. Consider adding a DOI via Zenodo for formal citation.

Please cite it as follows:

> **The HCSN Research Group, @hcsn. (2025). The Holographic Computational Spin-Network (HCSN): Theory & Simulation (Version 1.0.0) [Computer software]. https://github.com/hcsn-theory/HCSN-Theory**

### BibTeX Entry
For LaTeX/Overleaf users:
```bibtex
@software{HCSN2025,
  author = {The HCSN Research Group, @hcsn.},
  title = {The Holographic Computational Spin-Network (HCSN): Theory & Simulation},
  version = {1.0.0},
  year = {2025},
  url = {[https://github.com/hcsn-theory/HCSN-Theory](https://github.com/hcsn-theory/HCSN-Theory)}
}
```
---

## License & Contact 

This project is active research and published under Apache 2.0 licence. For collaboration or questions, open an issue or contact the maintainers via GitHub: [hcsn-theory](https://github.com/hcsn-theory) 

---
## 🏛️ Governance
The HCSN Research Group is maintained by **@hcsn**.

---
Philosophy
> “The universe may not be described by computation — it may be computation.”
---
HCSN treats this as a testable hypothesis: build minimal computational rules and examine what emerges.

Enjoy exploring! 🧩
