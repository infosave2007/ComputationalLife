#!/usr/bin/env python3
"""Micro-benchmarks for the hot numerical paths, emitted in the
`customSmallerIsBetter` JSON format that github-action-benchmark tracks over
time (see .github/workflows/ci.yml). Deterministic (fixed seeds); prints JSON
to stdout.

    python benchmarks/run_benchmarks.py > benchmark.json
"""

from __future__ import annotations

import json
import math
import time

import numpy as np

from complife import common, induction, quantum, replication


def timed(fn, repeat: int = 3) -> float:
    """Best-of-`repeat` wall time in milliseconds (best = least noisy)."""
    best = math.inf
    for _ in range(repeat):
        t0 = time.perf_counter()
        fn()
        best = min(best, time.perf_counter() - t0)
    return round(best * 1000.0, 4)


def main() -> int:
    sigma = math.e
    rng = np.random.default_rng(0)
    sample = rng.integers(0, 1 << 14, size=2_000_000, dtype=np.int64)
    lcg = induction.lcg_sequence(5000)
    qrng = np.random.default_rng(1)
    pairs = [(quantum.qubit(a, b), quantum.qubit(c, d))
             for a, b, c, d in qrng.uniform(0.3, 2.5, size=(500, 4))]

    benches = [
        ("quasispecies_eigenvector_L150",
         lambda: replication.quasispecies_distribution(sigma, 150, 0.02)),
        ("hamming_transition_matrix_L200",
         lambda: replication.hamming_transition_matrix(200, 0.01)),
        ("entropy_miller_madow_2M",
         lambda: common.entropy_from_samples(sample, 1 << 14)),
        ("mdl_codelen_lcg_5000",
         lambda: induction.mdl_codelen(lcg, 256)),
        ("no_cloning_500_pairs",
         lambda: [quantum.inner_product_obstruction(a, b) for a, b in pairs]),
    ]

    results = [{"name": name, "unit": "ms", "value": timed(fn)} for name, fn in benches]
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
