"""Shared numerics and reporting for the Computational Life modules.

Nothing here is domain-specific: it is the small toolkit the four modules reuse
— physical constants, entropy estimators (with bias correction and bootstrap
confidence intervals), and helpers for printing self-verifying reports and
snapshotting headline numbers to ``results/`` so tests can pin them.

All estimators operate on *count vectors* (histograms). Keeping the statistics
separate from the sampling makes them independently testable.
"""

from __future__ import annotations

import json
import math
import os
from collections.abc import Iterable, Sequence

import numpy as np

# --------------------------------------------------------------------------- #
#  Physical constants (SI), shared by physical_limits.py
# --------------------------------------------------------------------------- #
KB = 1.380649e-23            # Boltzmann constant, J/K
HBAR = 1.054571817e-34       # reduced Planck constant, J*s
H_PLANCK = 2.0 * math.pi * HBAR  # Planck constant h, J*s
C = 2.99792458e8             # speed of light, m/s
G = 6.67430e-11              # gravitational constant, m^3 kg^-1 s^-2
LN2 = math.log(2.0)
L_PLANCK = math.sqrt(HBAR * G / C**3)   # Planck length, ~1.616e-35 m
M_SUN = 1.98847e30           # solar mass, kg
MEV = 1.602176634e-13        # 1 MeV in joules

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(REPO_ROOT, "results")


# --------------------------------------------------------------------------- #
#  Formatting
# --------------------------------------------------------------------------- #
def fmt_pow2(log_bits: float) -> str:
    """Render ``2**log_bits`` without materialising astronomically large ints."""
    lb = float(log_bits)
    if lb <= 64:
        return f"2^{int(lb)} = {2 ** int(lb):,}"
    log10 = lb * math.log10(2.0)
    exp10 = int(log10)
    mant = 10.0 ** (log10 - exp10)
    return f"2^{int(lb)} (~{mant:.2f}e{exp10})"


def fmt_sci(x: float, sig: int = 3) -> str:
    """Compact scientific notation."""
    return f"{x:.{sig}e}"


def rule(char: str = "=", width: int = 78) -> str:
    return char * width


def header(title: str, char: str = "=", width: int = 78) -> str:
    return f"{rule(char, width)}\n{title}\n{rule(char, width)}"


# --------------------------------------------------------------------------- #
#  Entropy estimators (all in bits), operating on count vectors
# --------------------------------------------------------------------------- #
def _counts_array(counts: Iterable[int]) -> np.ndarray:
    c = np.asarray(list(counts) if not isinstance(counts, np.ndarray) else counts,
                   dtype=np.float64)
    return c[c > 0]


def entropy_plugin(counts: Iterable[int]) -> float:
    """Maximum-likelihood (plug-in) entropy in bits. Biased low."""
    c = _counts_array(counts)
    n = c.sum()
    if n == 0:
        return 0.0
    p = c / n
    return float(-np.sum(p * np.log2(p)))


def entropy_miller_madow(counts: Iterable[int]) -> float:
    """Plug-in entropy plus the Miller-Madow bias correction ``(K-1)/(2n ln2)``.

    ``K`` is the number of *observed* categories. This can only raise the
    plug-in estimate, so it is a mild, one-sided correction.
    """
    c = _counts_array(counts)
    n = c.sum()
    if n == 0:
        return 0.0
    k_obs = c.size
    return entropy_plugin(counts) + (k_obs - 1) / (2.0 * n * LN2)


def entropy_grassberger(counts: Iterable[int]) -> float:
    """Grassberger (2003) entropy estimator in bits.

    ``H = log2(n) - (1/n) * sum_k c_k * G(c_k)`` with ``G(c) = psi(c) + ...``
    A stronger, nearly-unbiased alternative to Miller-Madow; used as an
    independent cross-check. Implemented via ``digamma`` when SciPy is present,
    otherwise a high-accuracy series so the module keeps working numpy-only.
    """
    c = _counts_array(counts)
    n = c.sum()
    if n == 0:
        return 0.0
    g = _digamma(c) + 0.5 * (-1.0) ** c / (c * (c + 1.0))
    h_nats = math.log(n) - float(np.sum(c * g)) / n
    return h_nats / LN2


def _digamma(x: np.ndarray) -> np.ndarray:
    """Vectorised digamma. Uses SciPy if available, else an asymptotic series
    with recurrence shifting so it is accurate for small positive integers."""
    try:
        from scipy.special import digamma  # type: ignore

        return digamma(x)
    except Exception:
        x = np.asarray(x, dtype=np.float64).copy()
        result = np.zeros_like(x)
        # Shift up to x >= 6 using psi(x) = psi(x+1) - 1/x.
        while np.any(x < 6.0):
            mask = x < 6.0
            result[mask] -= 1.0 / x[mask]
            x[mask] += 1.0
        # Asymptotic expansion for x >= 6.
        inv = 1.0 / x
        inv2 = inv * inv
        result += (
            np.log(x)
            - 0.5 * inv
            - inv2 * (1.0 / 12.0 - inv2 * (1.0 / 120.0 - inv2 / 252.0))
        )
        return result


def bootstrap_entropy_ci(
    counts: Sequence[int],
    n: int | None = None,
    *,
    estimator=entropy_miller_madow,
    B: int = 1000,
    alpha: float = 0.05,
    seed: int = 0,
) -> tuple[float, float, float]:
    """Parametric (multinomial) bootstrap CI for an entropy estimate.

    Resamples counts ``B`` times from the empirical pmf and returns
    ``(point, lo, hi)`` where ``[lo, hi]`` is the ``1-alpha`` percentile
    interval of the estimator.
    """
    c = np.asarray(counts, dtype=np.float64)
    total = int(c.sum()) if n is None else int(n)
    p = c / c.sum()
    point = estimator(c)
    rng = np.random.default_rng(seed)
    boot = np.empty(B, dtype=np.float64)
    for b in range(B):
        resampled = rng.multinomial(total, p)
        boot[b] = estimator(resampled)
    lo = float(np.percentile(boot, 100 * (alpha / 2)))
    hi = float(np.percentile(boot, 100 * (1 - alpha / 2)))
    return point, lo, hi


def entropy_from_samples(values: np.ndarray, k: int,
                         estimator=entropy_miller_madow) -> float:
    """Estimate the entropy (bits) of an integer sample over ``k`` categories."""
    counts = np.bincount(np.asarray(values, dtype=np.int64), minlength=k)
    return estimator(counts)


def conditional_entropy_deterministic(t_vals: np.ndarray, m_vals: np.ndarray,
                                      kt: int, km: int,
                                      estimator=entropy_miller_madow) -> float:
    """Estimate ``H(T | M)`` when ``M = g(T)`` is a deterministic function of T.

    For deterministic ``M`` we have ``H(T, M) = H(T)`` and ``H(M | T) = 0``, so
    ``H(T | M) = H(T) - H(M)``. This identity is what makes the data-processing
    bound ``H(T|M) >= H(T) - b_M`` reduce to ``H(M) <= b_M``.
    """
    h_t = entropy_from_samples(t_vals, kt, estimator)
    h_m = entropy_from_samples(m_vals, km, estimator)
    return h_t - h_m


# --------------------------------------------------------------------------- #
#  Result snapshots (provenance): headline numbers -> results/<name>.json
# --------------------------------------------------------------------------- #
def save_result(name: str, payload: dict) -> str:
    """Write a module's headline numbers to ``results/<name>.json`` (sorted,
    rounded floats) and return the path. Tests recompute and compare."""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, f"{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(_roundtrip(payload), f, indent=2, sort_keys=True)
        f.write("\n")
    return path


def load_result(name: str) -> dict | None:
    path = os.path.join(RESULTS_DIR, f"{name}.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _roundtrip(obj):
    """Recursively coerce numpy scalars/arrays to JSON-friendly Python types."""
    if isinstance(obj, dict):
        return {k: _roundtrip(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_roundtrip(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return _roundtrip(obj.tolist())
    if isinstance(obj, np.generic):   # any numpy scalar: bool_, int64, float64, ...
        return _roundtrip(obj.item())
    if isinstance(obj, bool):
        return bool(obj)
    if isinstance(obj, float):
        return float(obj)
    if isinstance(obj, int):
        return int(obj)
    return obj


# --------------------------------------------------------------------------- #
#  Tiny self-verifying report harness
# --------------------------------------------------------------------------- #
class Report:
    """Accumulates PASS/FAIL checks so a demo both prints and self-verifies.

    ``check(label, condition)`` records and prints an assertion; ``ok`` is True
    iff every recorded check passed. Demos use this instead of bare ``assert``
    so the narrative and the verification stay in lock-step and a single demo
    can report several independent checks.
    """

    def __init__(self) -> None:
        self.checks: list[tuple[str, bool]] = []

    def check(self, label: str, condition: bool, *, verbose: bool = True) -> bool:
        cond = bool(condition)
        self.checks.append((label, cond))
        if verbose:
            print(f"   [{'PASS' if cond else 'FAIL'}] {label}")
        return cond

    @property
    def ok(self) -> bool:
        return all(c for _, c in self.checks)

    def summary(self) -> str:
        n = len(self.checks)
        passed = sum(1 for _, c in self.checks if c)
        return f"{passed}/{n} checks passed"
