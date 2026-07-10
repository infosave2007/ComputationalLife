"""Tests for the shared entropy estimators and helpers."""

import math

import numpy as np
import pytest

from complife import common


def test_entropy_uniform_is_log2_k():
    counts = np.full(256, 1000)  # perfectly uniform over 256 categories
    # plug-in is exact on an exactly-uniform histogram; the bias-corrected
    # estimators add a small (correct) positive term for finite n.
    assert common.entropy_plugin(counts) == pytest.approx(8.0, abs=1e-9)
    assert common.entropy_miller_madow(counts) == pytest.approx(8.0, abs=1e-2)
    assert common.entropy_miller_madow(counts) >= 8.0  # correction is one-sided
    assert common.entropy_grassberger(counts) == pytest.approx(8.0, abs=1e-2)


def test_entropy_deterministic_is_zero():
    counts = np.zeros(16)
    counts[3] = 5000
    assert common.entropy_plugin(counts) == pytest.approx(0.0, abs=1e-12)
    assert common.entropy_miller_madow(counts) == pytest.approx(0.0, abs=1e-12)


def test_miller_madow_never_below_plugin():
    rng = np.random.default_rng(0)
    for _ in range(20):
        counts = rng.integers(0, 50, size=32)
        assert common.entropy_miller_madow(counts) >= common.entropy_plugin(counts) - 1e-12


def test_grassberger_less_biased_than_plugin_undersampled():
    # Undersampled uniform: plug-in is biased low; Grassberger corrects.
    rng = np.random.default_rng(1)
    k = 1024
    samples = rng.integers(0, k, size=4000)
    counts = np.bincount(samples, minlength=k)
    true_H = math.log2(k)
    plugin = common.entropy_plugin(counts)
    grass = common.entropy_grassberger(counts)
    assert abs(grass - true_H) <= abs(plugin - true_H) + 1e-9


def test_bootstrap_ci_brackets_truth():
    # Well-sampled uniform-over-64: the CI is tight and brackets the true 6 bits.
    # (The point estimate may sit near an edge because of estimator bias; the CI
    # is a statement about sampling variance, so we test it against the truth.)
    rng = np.random.default_rng(2)
    counts = rng.multinomial(1_000_000, np.full(64, 1 / 64))
    point, lo, hi = common.bootstrap_entropy_ci(counts, 1_000_000, B=300, seed=0)
    assert lo < hi
    assert hi - lo < 0.01
    assert lo - 0.01 <= 6.0 <= hi + 0.01


def test_conditional_entropy_deterministic_identity():
    # M = g(T) with a 2-to-1 map: H(T|M) = H(T) - H(M).
    rng = np.random.default_rng(3)
    t = rng.integers(0, 8, size=200000)
    m = t >> 1  # 4 buckets
    cond = common.conditional_entropy_deterministic(t, m, 8, 4)
    h_t = common.entropy_from_samples(t, 8)
    h_m = common.entropy_from_samples(m, 4)
    assert cond == pytest.approx(h_t - h_m, abs=1e-9)
    assert cond == pytest.approx(1.0, abs=0.02)  # one lost bit


def test_physical_constants_sane():
    assert common.KB == pytest.approx(1.380649e-23)
    assert common.C == pytest.approx(2.99792458e8)
    assert common.L_PLANCK == pytest.approx(1.616e-35, rel=1e-2)
    assert common.H_PLANCK == pytest.approx(6.626e-34, rel=1e-3)
