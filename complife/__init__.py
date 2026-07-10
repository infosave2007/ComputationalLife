"""Computational Life — a computational theory of life and mind.

Four self-contained, adversarially verified modules:

* :mod:`complife.self_reference`  — Kleene's recursion theorem: self-reference
  exists in every Turing-complete language and costs only an additive constant.
* :mod:`complife.self_model`      — Conant–Ashby good regulator + the corollary
  that a self-inclusive model must be a lossy compression.
* :mod:`complife.replication`     — von Neumann's dual-use tape and Eigen's
  quasispecies error threshold.
* :mod:`complife.physical_limits` — Landauer / Bekenstein / holographic / speed
  ceilings, plus the one honest contact point with NVG physics.

Everything is substrate-independent information theory and cybernetics; physics
enters only as ceilings on the hardware (module 4).
"""

__version__ = "0.2.0"

__all__ = [
    "self_reference",
    "self_model",
    "replication",
    "physical_limits",
    "common",
]
