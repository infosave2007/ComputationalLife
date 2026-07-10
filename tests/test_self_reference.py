"""Tests for module 01 -- self-reference / Kleene recursion theorem."""

import hashlib

import pytest

from complife import self_reference as sr


# ---- fast: no subprocess ---------------------------------------------------
def test_underload_quine():
    assert sr.run_underload(sr.UNDERLOAD_QUINE) == sr.UNDERLOAD_QUINE
    assert len(sr.UNDERLOAD_QUINE) == 10


def test_lisp_quine():
    _, ok = sr.verify_lisp()
    assert ok


def test_brainfuck_hello_world():
    assert sr.run_bf(sr.BF_HELLO) == b"Hello World!\n"


def test_repr_overhead_is_159_plus_escapes():
    for row in sr.characterise_repr_overhead():
        assert row["overhead"] == 159 + row["escapes"]
        assert row["base_const"] == 159


def test_self_read_overhead_constant_across_payloads():
    # Overhead is len(sentinel)+len(tail) regardless of payload CONTENT.
    payloads = [b"", b"x=1", b"y=1  # " + b"\\" * 100, b"z=1  # '\"'\n"]
    overheads = {len(sr.augment_via_self_read(p)) - len(p) for p in payloads}
    assert len(overheads) == 1


def test_self_modifier_is_valid_python_and_fixed_width():
    g0, g1 = sr.self_modifier(0), sr.self_modifier(1)
    compile(g0, "<g0>", "exec")            # must be syntactically valid
    assert len(g0) == len(g1)              # fixed-width counter
    diffs = sum(1 for a, b in zip(g0, g1) if a != b)
    assert diffs <= 3                      # only the 3 counter digits


# ---- slow: spawn subprocesses ---------------------------------------------
@pytest.mark.slow
def test_python_quine_reproduces():
    n, ok = sr.verify_python_quine()
    assert ok and n == 75


@pytest.mark.slow
def test_second_recursion_theorem_all_g():
    for name, ok in sr.verify_second_recursion_theorem():
        assert ok, f"program failed to output {name}(own_source)"


@pytest.mark.slow
def test_second_recursion_theorem_sha256_value():
    src = sr.build_self_applying(sr.G_FUNCTIONS["sha256"])
    out = sr._run_bytes(src.encode()).decode()
    assert out == hashlib.sha256(src.encode()).hexdigest()


@pytest.mark.slow
def test_self_modification_counter_and_invariance():
    counter_ok, invariant_ok = sr.verify_self_modification(k=4)
    assert counter_ok and invariant_ok


@pytest.mark.slow
def test_self_read_programs_reproduce_source():
    _, ok = sr.measure_self_read_overhead()
    assert ok


@pytest.mark.slow
def test_rice_theorem_every_decider_refuted():
    results = sr.verify_rice()
    assert len(results) >= 4
    for name, refuted in results:
        assert refuted, f"decider {name} was not refuted by its diagonal"
