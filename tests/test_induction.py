"""Tests for module 06 -- Solomonoff / MDL: prediction = compression."""


import numpy as np
import pytest

from complife import induction as ind


def test_lcg_is_recovered_and_reproduces():
    seq = ind.lcg_sequence(500, a=137, c=13, m=256, seed=5)
    ac = ind.infer_lcg(seq, m=256)
    assert ac is not None
    a, c = ac
    # the recovered generator reproduces the whole sequence
    x = int(seq[0])
    for i in range(1, len(seq)):
        x = (a * x + c) % 256
        assert x == int(seq[i])


def test_mdl_beats_statistics_on_algorithmic_data():
    n = 3000
    for seq, alph in [(ind.lcg_sequence(n), 256),
                      (ind.thue_morse(n), 2),
                      (ind.periodic_sequence(n, list(range(9))), 256)]:
        stat, _ = ind.best_statistical_codelen(seq, alph)
        mdl, name = ind.mdl_codelen(seq, alph)
        assert mdl < 0.25 * stat          # order-of-magnitude better
        assert not name.startswith("statistical")   # a real program was found


def test_true_randomness_is_incompressible():
    seq = ind.random_bytes(3000, seed=3)
    mdl, name = ind.mdl_codelen(seq, 256)
    # no short program fits -> falls back to ~log2(256) = 8 bits/symbol
    assert mdl / len(seq) > 0.95 * 8.0
    assert name.startswith("statistical")


def test_two_part_code_compresses_lcg():
    n = 2000
    seq = ind.lcg_sequence(n)
    mdl, _ = ind.mdl_codelen(seq, 256)
    assert (n * 8.0) / mdl > 100          # >100x vs raw bytes


def test_statistical_codelen_matches_entropy_on_iid():
    # order-0 code length on a fair coin ~ n bits.
    rng = np.random.default_rng(0)
    seq = rng.integers(0, 2, size=5000)
    bits = ind.codelen_statistical(seq, order=0, alphabet=2)
    assert bits / len(seq) == pytest.approx(1.0, abs=0.02)


@pytest.mark.slow
def test_demo_runs_green(capsys):
    assert ind.demo()
    assert "ALL CHECKS PASSED" in capsys.readouterr().out
