"""Tests for module 03 -- von Neumann replicator & Eigen quasispecies."""

import math

import numpy as np
import pytest

from complife import replication as rep


# ---- Part A: the replicator -----------------------------------------------
def test_replicator_child_and_grandchild_identical():
    parent = rep.build_organism(rep.MACHINERY, "GENE_v1_AAAAAAAA")
    ns = {}
    exec(rep.MACHINERY, ns)
    child = ns["replicate"](parent)
    assert child == parent
    grandchild = rep.replicate_via_own_machinery(child)
    assert grandchild == child == parent


def test_mutation_inherited_verbatim():
    parent = rep.build_organism(rep.MACHINERY, "GENE_v1_AAAAAAAA")
    ns = {}
    exec(rep.MACHINERY, ns)
    mutant, pos = rep.mutate_payload(parent)
    assert rep.hamming(mutant, parent) == 1
    mut_child = ns["replicate"](mutant)
    assert mut_child == mutant
    assert rep.hamming(mut_child, parent) == 1


def test_machinery_independent_of_payload_length():
    p1 = rep.build_organism(rep.MACHINERY, "AAAA")
    p2 = rep.build_organism(rep.MACHINERY, "AAAA" * 25)
    assert p1.split(rep.SEP1, 1)[0] == p2.split(rep.SEP1, 1)[0]


# ---- Part B1: threshold solver (the fixed bug) ----------------------------
def test_critical_mu_closed_form_matches_numeric():
    sigma = math.e
    for L in (50, 100, 500, 1000, 5000):
        assert rep.critical_mu(sigma, L) == pytest.approx(
            rep.critical_mu_numeric(sigma, L), abs=1e-9)


def test_threshold_approaches_ln_sigma_from_below_monotone():
    sigma = math.e
    muLs = [rep.critical_mu(sigma, L) * L for L in (50, 100, 500, 1000, 5000)]
    assert all(x < math.log(sigma) for x in muLs)        # strictly below
    assert all(b > a for a, b in zip(muLs, muLs[1:]))     # monotone increasing


def test_master_fraction_2c_survival_and_collapse():
    sigma, L = math.e, 100
    assert rep.master_fraction_2c(0.5 / L, L, sigma) > 0
    assert rep.master_fraction_2c(2.0 / L, L, sigma) == 0.0


@pytest.mark.parametrize("sigma", [1.5, 2.0, math.e, 5.0])
def test_threshold_general_sigma(sigma):
    # mu_crit*L -> ln(sigma) with O(1/L) error, for a RANGE of sigma (not just e).
    muL = rep.critical_mu(sigma, 2000) * 2000
    assert abs(muL - math.log(sigma)) < math.log(sigma) ** 2 / (2 * 2000) + 1e-6


# ---- Part B2: full quasispecies vs brute force ----------------------------
def test_transition_matrix_column_stochastic():
    Q = rep.hamming_transition_matrix(10, 0.07)
    assert np.allclose(Q.sum(axis=0), 1.0)
    assert np.all(Q >= 0)


@pytest.mark.parametrize("L,mu", [(6, 0.05), (8, 0.05), (10, 0.08)])
def test_lumped_quasispecies_matches_bruteforce(L, mu):
    sigma = math.e
    p_lump, _ = rep.quasispecies_distribution(sigma, L, mu)
    p_bf = rep.quasispecies_bruteforce(sigma, L, mu)
    assert np.max(np.abs(p_lump - p_bf)) < 1e-10
    assert p_lump.sum() == pytest.approx(1.0)


def test_full_model_master_fraction_smooth_positive():
    # With back-mutation the master fraction is strictly > 0 at finite L,
    # even past the 2-compartment 'catastrophe'.
    sigma, L = math.e, 40
    for muL in (0.5, 1.0, 1.5, 2.0):
        p, _ = rep.quasispecies_distribution(sigma, L, muL / L)
        assert p[0] > 0.0


# ---- Part B3: exact Wright-Fisher -----------------------------------------
@pytest.mark.slow
def test_wright_fisher_persists_and_collapses():
    sigma, L = math.e, 100
    _, mean_lo, _ = rep.wf_survival_curve(0.5 / L, L, sigma, N=100_000,
                                          gens=300, reps=8, seed=0)
    _, mean_hi, _ = rep.wf_survival_curve(2.0 / L, L, sigma, N=100_000,
                                          gens=300, reps=8, seed=0)
    assert mean_lo > 0.05
    assert mean_hi < 0.01
