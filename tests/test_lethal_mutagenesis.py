"""Tests for module 07 -- the lethal-mutagenesis calculator (application of 03)."""

import math

import pytest

from complife import lethal_mutagenesis as lm


def test_fold_increase_matches_threshold():
    # At mu*L = ln(sigma) the fold is exactly 1 (already at the cliff).
    sigma = math.e
    L, mu = 10_000, math.log(sigma) / 10_000
    assert lm.fold_increase_to_catastrophe(L, mu, sigma) == pytest.approx(1.0, rel=1e-9)


def test_rna_viruses_near_edge_coronavirus_far():
    # Non-proofreading RNA viruses sit within a few-fold of the catastrophe;
    # a proofreading coronavirus sits far below it.
    polio = lm.report_for("polio", 7_500, 1.0e-4)
    cov = lm.report_for("cov", 29_900, 1.0e-6)
    assert polio["fold_to_catastrophe"] < 3
    assert cov["fold_to_catastrophe"] > 10


def test_max_stable_genome_scales_inverse_mu():
    assert lm.max_stable_genome(1e-4) == pytest.approx(math.log(math.e) / 1e-4)
    assert lm.max_stable_genome(1e-6) > lm.max_stable_genome(1e-4)


def test_past_catastrophe_flag():
    r = lm.report_for("dead", 20_000, 1.0e-3)   # mu*L = 20 >> 1
    assert r["past_catastrophe"]
    assert r["fold_to_catastrophe"] < 1.0


@pytest.mark.slow
def test_demo_runs_green(capsys):
    assert lm.demo()
    assert "ALL CHECKS PASSED" in capsys.readouterr().out
