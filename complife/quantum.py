#!/usr/bin/env python3
"""The fifth wall: quantum states cannot be copied (no-cloning).

Module 03 shows *classical* self-copying is easy and cheap. Quantum information
draws the opposite line: an unknown quantum state **cannot be copied at all**.
This is not a technological limitation — it is forced by the linearity of
quantum mechanics, and we demonstrate it two independent ways in plain linear
algebra (numpy), then contrast it with the classical case.

  1. LINEARITY obstruction: a copier fixed on the basis (|0>->|00>, |1>->|11>)
     is *forced* by linearity to turn a superposition into an ENTANGLED pair,
     not a copy. We compute the fidelity and watch it fall from 1 to 1/2.
  2. INNER-PRODUCT obstruction: any cloning unitary would need
     <psi|phi> = <psi|phi>^2 for all pairs, so states must be orthogonal or
     identical — no cloner works for general (non-orthogonal) states.

The honest contrast: classical bits (basis states) copy perfectly; it is
*superpositions of unknown states* that cannot. Copying is cheap classically,
impossible quantumly.
"""

from __future__ import annotations

import cmath
import math

import numpy as np

from .common import Report, header, save_result

# --------------------------------------------------------------------------- #
#  Qubit helpers (state vectors as length-2 complex numpy arrays)
# --------------------------------------------------------------------------- #
KET0 = np.array([1.0 + 0j, 0.0 + 0j])
KET1 = np.array([0.0 + 0j, 1.0 + 0j])
KETP = (KET0 + KET1) / math.sqrt(2)          # |+> = (|0>+|1>)/sqrt2
KETM = (KET0 - KET1) / math.sqrt(2)          # |->

# CNOT on 2 qubits (control = first), the natural "copy the basis" gate.
CNOT = np.array([
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 0, 1],
    [0, 0, 1, 0],
], dtype=complex)


def qubit(theta: float, phi: float) -> np.ndarray:
    """A general pure qubit cos(theta/2)|0> + e^{i phi} sin(theta/2)|1>."""
    return np.array([math.cos(theta / 2),
                     cmath.exp(1j * phi) * math.sin(theta / 2)])


def overlap(a: np.ndarray, b: np.ndarray) -> complex:
    """Inner product <a|b>."""
    return complex(np.vdot(a, b))


def fidelity_to_product(joint: np.ndarray, target: np.ndarray) -> float:
    """|<target (x) target | joint>|^2 -- how close a 2-qubit state is to a
    perfect clone target (x) target."""
    tt = np.kron(target, target)
    return float(abs(np.vdot(tt, joint)) ** 2)


# --------------------------------------------------------------------------- #
#  1. Linearity obstruction: the basis-copier entangles superpositions
# --------------------------------------------------------------------------- #
def clone_attempt_cnot(psi: np.ndarray) -> np.ndarray:
    """Feed psi (x) |0> through CNOT -- the gate that copies |0>,|1> perfectly."""
    return CNOT @ np.kron(psi, KET0)


def clone_fidelity(psi: np.ndarray) -> float:
    """How well CNOT clones psi (1.0 = perfect copy)."""
    return fidelity_to_product(clone_attempt_cnot(psi), psi)


def linearity_forces_entanglement() -> tuple[float, np.ndarray, np.ndarray]:
    """By linearity, clone(|+>) = (clone|0> + clone|1>)/sqrt2 = (|00>+|11>)/sqrt2,
    a Bell state, NOT |+>|+>. Return (fidelity, cnot_output, bell_state)."""
    out = clone_attempt_cnot(KETP)
    bell = (np.kron(KET0, KET0) + np.kron(KET1, KET1)) / math.sqrt(2)
    return fidelity_to_product(out, KETP), out, bell


# --------------------------------------------------------------------------- #
#  2. Inner-product obstruction: <psi|phi> = <psi|phi>^2 has no middle ground
# --------------------------------------------------------------------------- #
def inner_product_obstruction(psi: np.ndarray, phi: np.ndarray) -> dict:
    """A cloning unitary preserves inner products, forcing
    <psi|phi> = <psi|phi>^2, i.e. the overlap must be 0 or 1. Any other value
    is a contradiction -> no cloner exists for that pair."""
    s = overlap(psi, phi)
    return {
        "overlap": abs(s),
        "overlap_sq": abs(s * s),
        "consistent": abs(abs(s) - abs(s * s)) < 1e-9,  # True only if |s| in {0,1}
    }


# --------------------------------------------------------------------------- #
#  3. Classical contrast: basis (classical) states DO copy
# --------------------------------------------------------------------------- #
def classical_copy_works() -> bool:
    """CNOT clones the two classical basis states perfectly -- classical bits
    can be copied (this is what makes module 03's replicator possible)."""
    return (clone_fidelity(KET0) > 1 - 1e-12) and (clone_fidelity(KET1) > 1 - 1e-12)


# --------------------------------------------------------------------------- #
#  Demo
# --------------------------------------------------------------------------- #
def demo() -> bool:
    print(header("The fifth wall: quantum states cannot be copied (no-cloning)"))
    report = Report()

    print("\n1. CLASSICAL states copy perfectly (CNOT = 'copy the bit'):")
    for name, st in [("|0>", KET0), ("|1>", KET1)]:
        f = clone_fidelity(st)
        print(f"   clone {name}: fidelity = {f:.6f}")
    report.check("classical basis states |0>,|1> clone perfectly (fidelity=1)",
                 classical_copy_works())

    print("\n2. LINEARITY forbids cloning a superposition:")
    f_plus, out, bell = linearity_forces_entanglement()
    print(f"   clone |+>: fidelity to |+>|+> = {f_plus:.6f}  (perfect copy would be 1.0)")
    print("   instead the copier outputs the entangled Bell state (|00>+|11>)/sqrt2:")
    report.check("CNOT(|+>|0>) equals the Bell state (linearity, not a copy)",
                 float(np.max(np.abs(out - bell))) < 1e-12)
    report.check("cloning |+> fails: fidelity = 1/2 (not 1)", abs(f_plus - 0.5) < 1e-9)

    print("\n3. INNER-PRODUCT obstruction: a cloner needs <psi|phi> = <psi|phi>^2")
    print("   overlap   overlap^2   consistent?")
    rng = np.random.default_rng(0)
    # orthogonal and identical pairs are the ONLY consistent ones
    demo_pairs = [("|0>,|1> (orthogonal)", KET0, KET1),
                  ("|+>,|+> (identical)", KETP, KETP),
                  ("|0>,|+> (non-orthogonal)", KET0, KETP),
                  ("|+>,|-> (orthogonal)", KETP, KETM)]
    for label, a, b in demo_pairs:
        r = inner_product_obstruction(a, b)
        print(f"   {label:26s} {r['overlap']:.4f}    {r['overlap_sq']:.4f}     {r['consistent']}")
    # random non-orthogonal pairs are NEVER consistent -> no cloner
    n_random = 2000
    n_inconsistent = 0
    for _ in range(n_random):
        a = qubit(rng.uniform(0.2, math.pi - 0.2), rng.uniform(0, 2 * math.pi))
        b = qubit(rng.uniform(0.2, math.pi - 0.2), rng.uniform(0, 2 * math.pi))
        r = inner_product_obstruction(a, b)
        s = r["overlap"]
        if 1e-3 < s < 1 - 1e-3 and not r["consistent"]:
            n_inconsistent += 1
    frac = n_inconsistent / n_random
    print(f"   over {n_random} random non-orthogonal pairs: "
          f"{100 * frac:.1f}% violate <psi|phi>=<psi|phi>^2 => NO cloner exists")
    report.check("no cloning unitary for non-orthogonal states (inner-product proof)",
                 frac > 0.95)

    # Optimal *approximate* universal cloner is capped at fidelity 5/6 for qubits.
    print("\n   (Even the best *approximate* universal qubit cloner is capped at "
          "fidelity 5/6 ≈ 0.833 — a known bound.)")

    print("\n" + header("CONCLUSION"))
    print("Classical information (basis states) copies for free — that is exactly what")
    print("lets a von Neumann replicator exist (module 03). An UNKNOWN quantum state")
    print("cannot be copied at all: linearity turns a copy attempt into entanglement,")
    print("and unitarity forbids it for any non-orthogonal pair. Copying is cheap")
    print("classically, and a hard wall quantumly — the fifth impossibility here.")
    print(f"\n{report.summary()}")
    print("ALL CHECKS PASSED" if report.ok else "SOME CHECKS FAILED")

    save_result("05_quantum", {
        "clone_fidelity_basis": clone_fidelity(KET0),
        "clone_fidelity_plus": f_plus,
        "noncloning_fraction": frac,
        "all_checks_passed": report.ok,
    })
    return report.ok


if __name__ == "__main__":
    raise SystemExit(0 if demo() else 1)
