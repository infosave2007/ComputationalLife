"""End-to-end smoke tests: every module runs green (the repo's headline claim).

These exercise the full demos (Monte-Carlo + subprocesses), so they are slow.
Run with `pytest` (full) or skip with `pytest -m "not slow"`.
"""

import pytest

from complife import (
    induction,
    physical_limits,
    quantum,
    replication,
    self_model,
    self_reference,
)


@pytest.mark.slow
@pytest.mark.parametrize("demo", [
    self_reference.demo,
    self_model.demo,
    replication.demo,
    physical_limits.demo,
    quantum.demo,
    induction.demo,
], ids=["self_reference", "self_model", "replication", "physical_limits",
        "quantum", "induction"])
def test_demo_all_checks_pass(demo, capsys):
    ok = demo()
    captured = capsys.readouterr()
    assert ok, f"{demo.__module__} reported a failed check:\n{captured.out[-2000:]}"
    assert "ALL CHECKS PASSED" in captured.out


@pytest.mark.slow
def test_main_runs_all_modules():
    from complife.__main__ import main
    assert main([]) == 0
