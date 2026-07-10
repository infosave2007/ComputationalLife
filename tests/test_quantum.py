"""Tests for module 05 -- quantum no-cloning."""

import math

import numpy as np
import pytest

from complife import quantum as q


def test_classical_basis_states_clone():
    assert q.clone_fidelity(q.KET0) == pytest.approx(1.0, abs=1e-12)
    assert q.clone_fidelity(q.KET1) == pytest.approx(1.0, abs=1e-12)
    assert q.classical_copy_works()


def test_superposition_cannot_be_cloned_fidelity_half():
    # Linearity forces CNOT(|+>|0>) into a Bell state; fidelity to |+>|+> is 1/2.
    assert q.clone_fidelity(q.KETP) == pytest.approx(0.5, abs=1e-9)


def test_clone_attempt_is_the_bell_state():
    out = q.clone_attempt_cnot(q.KETP)
    bell = (np.kron(q.KET0, q.KET0) + np.kron(q.KET1, q.KET1)) / math.sqrt(2)
    assert np.max(np.abs(out - bell)) < 1e-12


def test_inner_product_obstruction():
    # orthogonal / identical are the only self-consistent overlaps.
    assert q.inner_product_obstruction(q.KET0, q.KET1)["consistent"]      # 0
    assert q.inner_product_obstruction(q.KETP, q.KETP)["consistent"]      # 1
    # a non-orthogonal pair violates <psi|phi> = <psi|phi>^2.
    r = q.inner_product_obstruction(q.KET0, q.KETP)
    assert not r["consistent"]
    assert r["overlap"] == pytest.approx(1 / math.sqrt(2), abs=1e-9)
    assert r["overlap_sq"] == pytest.approx(0.5, abs=1e-9)


def test_random_nonorthogonal_pairs_forbid_cloning():
    rng = np.random.default_rng(1)
    violations = 0
    trials = 500
    for _ in range(trials):
        a = q.qubit(rng.uniform(0.3, math.pi - 0.3), rng.uniform(0, 2 * math.pi))
        b = q.qubit(rng.uniform(0.3, math.pi - 0.3), rng.uniform(0, 2 * math.pi))
        r = q.inner_product_obstruction(a, b)
        if 1e-3 < r["overlap"] < 1 - 1e-3:
            assert not r["consistent"]
            violations += 1
    assert violations > 0.9 * trials


@pytest.mark.slow
def test_demo_runs_green(capsys):
    assert q.demo()
    assert "ALL CHECKS PASSED" in capsys.readouterr().out
