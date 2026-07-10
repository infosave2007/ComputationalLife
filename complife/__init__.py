"""Computational Life — a computational theory of life and mind.

Four self-contained, adversarially verified modules:

* :mod:`complife.self_reference`  — Kleene's recursion theorem: self-reference
  exists in every Turing-complete language and costs only an additive constant.
* :mod:`complife.self_model`      — Conant–Ashby good regulator + the corollary
  that a self-inclusive model must be a lossy compression.
* :mod:`complife.replication`     — von Neumann's dual-use tape and Eigen's
  quasispecies error threshold.
* :mod:`complife.physical_limits` — Landauer / Bekenstein / holographic / speed
  ceilings (incl. LLM inference vs the Landauer floor), plus the one honest
  contact point with NVG physics.
* :mod:`complife.quantum`         — the fifth wall: an unknown quantum state
  cannot be copied (no-cloning), contrasting classical self-copying.
* :mod:`complife.induction`       — prediction = compression: the shortest
  program wins (Solomonoff / MDL), with the incompressible-data boundary.

Everything is substrate-independent information theory and cybernetics; physics
enters only as ceilings on the hardware (module 4).
"""

__version__ = "0.3.2"

__all__ = [
    "self_reference",
    "self_model",
    "replication",
    "physical_limits",
    "quantum",
    "induction",
    "lethal_mutagenesis",
    "common",
]
