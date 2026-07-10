"""Tests for module 02 -- self-model lossiness & the good regulator."""

import numpy as np
import pytest

from complife import self_model as sm
from complife.common import entropy_from_samples


def test_analytic_impossibility_and_ratio():
    for ps in sm.PARAM_SETS:
        r = sm.analyse(ps)
        assert not r["exact_possible"]      # 2^b_M < |T|
        assert r["r_lt_1"]                  # compression ratio < 1
        assert r["Hcond_min"] == max(ps["H"] - ps["b_M"], 0)
        assert r["D_max"] == ps["B"] // ps["beta"]


def test_dpi_floor_holds_for_arbitrary_random_g():
    # The real content: H(M) <= b_M and H(T|M) >= H(T)-b_M for ANY g.
    H, n = 12, 400_000
    rng = np.random.default_rng(0)
    t, k, H_true = sm.uniform_source(H, n, rng)
    for b_M in (2, 4, 6, 8):
        for r in range(4):
            m, km = sm.random_hash_model(t, b_M, H, np.random.default_rng(100 + r))
            res = sm.dpi_check(t, m, km, H_true, b_M)
            assert res["H_M"] <= b_M + 1e-6          # I(T;M) = H(M) <= b_M
            assert res["H_cond"] >= res["floor"] - 0.05  # floor holds


def test_wasteful_g_sits_strictly_above_floor():
    H, n = 12, 400_000
    rng = np.random.default_rng(0)
    t, k, H_true = sm.uniform_source(H, n, rng)
    b_M = 10
    m, km = sm.random_hash_model(t, b_M, H, np.random.default_rng(7),
                                 distinct_bits=b_M - 3)
    res = sm.dpi_check(t, m, km, H_true, b_M)
    assert res["gap"] > 0.5


def test_greedy_beats_prefix_on_skewed_source():
    H, n = 12, 400_000
    rng = np.random.default_rng(0)
    t, k, H_true = sm.zipf_source(H, n, rng, s=1.2)
    pmf = np.bincount(t, minlength=k).astype(float)
    pmf /= pmf.sum()
    b_M = 6
    m_pref = sm.prefix_model(t, b_M, H)
    cond_pref = H_true - entropy_from_samples(m_pref, 1 << b_M)
    m_greedy, kg = sm.greedy_partition_model(t, pmf, b_M)
    cond_greedy = H_true - entropy_from_samples(m_greedy, kg)
    assert cond_greedy <= cond_pref + 1e-9   # greedy retains more variety
    assert cond_greedy >= H_true - b_M - 0.05  # floor still holds


def test_conant_ashby_optimal_regulator_is_a_model():
    n = 6
    p_D = [1.0 / n] * n
    minH, optimal = sm.optimal_regulator(lambda d, r: (d + r) % n, p_D, r=n)
    assert minH == pytest.approx(0.0, abs=1e-9)   # perfect regulation possible
    assert len(optimal) == n                       # unique up to goal relabeling
    for policy in optimal:                         # each is rho(D)=(c-D) mod n
        consts = {(policy[d] + d) % n for d in range(n)}
        assert len(consts) == 1


def test_conant_ashby_bit_budget_matches_self_model_floor():
    # A b-bit regulator on Z=(D+R) mod 2^k has residual H(Z) = k - b.
    import math
    from collections import defaultdict
    k = 3
    n = 1 << k
    for b in range(k + 1):
        shift = k - b
        zdist = defaultdict(float)
        for d in range(n):
            action = (-((d >> shift) << shift)) % n
            zdist[(d + action) % n] += 1.0 / n
        Hz = -sum(p * math.log2(p) for p in zdist.values() if p > 0)
        assert Hz == pytest.approx(k - b, abs=1e-9)
