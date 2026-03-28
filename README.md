# 🌀 HCSN — Hierarchical Causal Structure Network

[![DOI](https://img.shields.io/badge/DOI-10.55277%2Fresearchhub.fvahxvpt.1-blue)](https://doi.org/10.55277/researchhub.fvahxvpt.1)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0004--1698--5729-green.svg)](https://orcid.org/0009-0004-1698-5729)

---

> **HCSN** explores the hypothesis that the universe is fundamentally computational —
> built from discrete events and directed causal relations, with no assumed background space, time, or quantum framework.

📺 **[Watch the overview on YouTube →](https://youtu.be/A0oh6Rlx03Y)**
📄 **[Read the paper on ResearchHub →](https://doi.org/10.55277/researchhub.fvahxvpt.1)**

---

## ✨ Highlights

- 🔁 **Local rewrite rules** drive the evolution of a causal hypergraph
- 📐 **Geometry, time, and dimensionality** emerge — they are not assumed
- 🧲 **Particles** appear as persistent topological defects in the network
- 🔬 **Reproducible experiments** test emergence of Lorentz invariance, mass, and interaction
- 🎥 **Built-in visualizer** and Blender importer for 3D cinematic rendering

---

## 📋 Table of Contents

- [Overview](#overview)
- [Repository Structure](#repository-structure)
- [Quick Start](#quick-start)
- [How to Run Experiments](#how-to-run-experiments)
- [Diagnostics Explained](#diagnostics-explained)
- [Visualization](#visualization)
- [Current Research Focus](#current-research-focus)
- [Contributing](#contributing)
- [Citation](#citation)
- [License & Contact](#license--contact)

---

## Overview

HCSN proposes a discrete, causal, and computational substrate for physics:

- **Events** are vertices in a hypergraph; **causal relations** are directed hyperedges
- **Dynamics** are local probabilistic rewrite rules — no global clock, no background metric
- **Time** is the count of irreversible rewrites (rewrite depth)
- **Geometry, dimension, and particles** emerge from what statistically persists

The long-term goal is to identify the minimal rule set that produces universes consistent with:
- Lorentz invariance (emergent attractor)
- 4D spacetime-like structure
- Holographic scaling of information
- Quantum probabilistic behavior (Born rule from causal ignorance)

The companion theory repository is at [`hcsn-theory`](https://github.com/hcsn-theory/HCSN-core-Theory).

---

## Repository Structure

```text
hcsn-sim/
├── engine/                     # Core simulation engine
│   ├── hypergraph.py           # Vertices, hyperedges, causal ordering
│   ├── rules.py                # Rewrite rules
│   ├── rewrite_engine.py       # Acceptance dynamics and rewrite scheduling
│   ├── observables.py          # Physical diagnostic measurements
│   └── physics_params.py       # Shared physics parameters
│
├── sim-exp/                    # Reproducible experiments
│   ├── run_simulation.py       # Main simulation runner
│   ├── exp_critical_scan.py    # Phase transition scan
│   ├── exp_phase_diagram.py    # Omega phase diagram
│   ├── exp_long_critical_run.py
│   ├── exp_worldline_interactions.py
│   ├── scattering_experiment.py
│   ├── measure/                # Measurement scripts
│   ├── plot/                   # Plotting scripts
│   ├── tests/                  # Test suite
│   └── json/                   # Experiment output data
│
├── multiverse/                 # Multi-variant universe runs (universality tests)
│   ├── baseline/
│   ├── variant_1/ … variant_4/
│
├── analysis/                   # Legacy analysis scripts
├── visualizer.html             # Interactive browser-based visualizer
├── visualizer_server.py        # Local server for the visualizer
├── blender_importer.py         # Import cinematic frames into Blender
├── export_cinematic.py         # Export simulation to cinematic frame format
├── export_csv.py               # Export simulation data to CSV
├── cinematic_frames.json       # Pre-exported cinematic data
├── hcsn_sample.csv             # Sample simulation output
├── simulation.log              # Latest simulation log
└── requirements.txt            # Python dependencies
```

---

## Quick Start

**Requirements**
- Python 3.10 or later
- Dependencies: `pytest`, `websockets`, `asyncio`

```bash
pip install -r requirements.txt
```

**Clone and run:**

```bash
git clone https://github.com/hcsn-theory/hcsn-sim.git
cd hcsn-sim
python3 sim-exp/run_simulation.py
```

This runs a toy universe and prints diagnostics periodically.

---

## How to Run Experiments

The `sim-exp/` directory contains all reproducible experiments:

| Script | Purpose |
|--------|---------|
| `run_simulation.py` | Main simulation runner |
| `exp_critical_scan.py` | Scan Ω values to locate phase transition |
| `exp_phase_diagram.py` | Map defect rate across Ω regimes |
| `exp_long_critical_run.py` | Extended run at critical Ω |
| `exp_worldline_interactions.py` | Two-particle interaction experiment |
| `scattering_experiment.py` | Scattering geometry test |

**Key printed diagnostics (periodic):**
- average coordination ⟨k⟩
- causal depth (L)
- interaction concentration (Φ)
- closure density (Ψ)
- hierarchical stability (Ω)

---

## Diagnostics Explained

| Symbol | Name | Meaning | Target Range |
|:------:|:-----|:--------|:------------|
| ⟨k⟩ | Avg coordination | Controls effective dimensionality | ≈ 7.5–8.5 for spacetime-like geometry |
| L | Causal depth | Maximum causal chain length — emergent time | Grows with rewrites |
| Φ | Interaction concentration | Hub dominance (lower = more uniform) | Small Φ preferred |
| Ψ | Closure density | Redundancy in causal closure | Non-zero = error correction |
| Ω | Hierarchical closure | RG-like stability across scales | > 1.0 for persistent structure |

**Phase interpretation:**

| Ω Regime | Behavior |
|----------|----------|
| Ω < 1.0 (subcritical) | Transient defects, no stable transport |
| Ω ≈ 1.08–1.18 (critical) | Phase transition, marginal stability |
| Ω > 1.2 (supercritical) | Persistent worldlines, stable emergent structure |

---

## Visualization

HCSN includes a browser-based visualizer and a Blender pipeline for cinematic rendering:

**Browser Visualizer:**
```bash
python3 visualizer_server.py
# Open visualizer.html in your browser
```

**Blender 3D Import:**
1. Run `export_cinematic.py` to generate `cinematic_frames.json`
2. Import into Blender with `blender_importer.py`

**CSV Export:**
```bash
python3 export_csv.py
```

---

## Current Research Focus

Active directions:
- Prevent metric collapse under coarse-graining
- Implement logarithmic information metrics (holographic scaling tests)
- Enforce holographic bounds dynamically during evolution
- Search for Lorentz-invariant fixed points of the rewrite dynamics
- Derive quantum probabilistic behavior (Born rule) from causal ignorance

---

## Contributing

We welcome contributions from physicists, mathematicians, and programmers.

**Getting started:**
1. Fork the repo, create a feature branch
2. Add reproducible experiments under `sim-exp/`
3. Document new rules, diagnostics, and observed behaviors
4. Open a PR with clear description, expected behavior, and reproducibility notes

**Guidelines:**
- Seed all RNGs for reproducibility
- New rules or observables belong in `engine/`
- Keep experiments modular and self-contained

---

## Citation

If you use HCSN in your research, please cite both the paper and the software:

> Saif Mukhtar. *HCSN: A Hierarchical Causal Structure Network Framework for Emergent Physics.* ResearchHub, 2026. DOI: [10.55277/researchhub.fvahxvpt.1](https://doi.org/10.55277/researchhub.fvahxvpt.1)

**BibTeX:**
```bibtex
@article{mukhtar2026hcsn,
  author  = {Saif Mukhtar},
  title   = {HCSN: A Hierarchical Causal Structure Network Framework for Emergent Physics},
  year    = {2026},
  doi     = {10.55277/researchhub.fvahxvpt.1},
  url     = {https://doi.org/10.55277/researchhub.fvahxvpt.1}
}
```

---

## License & Contact

Published under the **Apache 2.0** licence.

For collaboration or questions, open an issue or contact via GitHub: [hcsn-theory](https://github.com/hcsn-theory)

---

## 🏛️ Governance

The HCSN Research Group is maintained by **[@hcsn](https://github.com/hcsn-theory)**.

---

> *"The universe may not be described by computation — it may be computation."*

HCSN treats this as a **testable hypothesis**: build minimal computational rules and examine what emerges.

Enjoy exploring! 🧩
