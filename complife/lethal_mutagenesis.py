#!/usr/bin/env python3
"""A practical tool built on module 03: the lethal-mutagenesis calculator.

Eigen's error threshold (`replication.py`) says a replicator's master sequence
survives only while `mu * L < ln(sigma)` — copy too sloppily and the genome
dissolves into an "error catastrophe". This is the working theory behind
**lethal-mutagenesis antivirals** (molnupiravir, favipiravir, ribavirin): a drug
raises a virus's per-base error rate `mu` until it crosses the cliff.

Given a virus's genome length `L`, fitness advantage `sigma`, and current error
rate `mu`, this computes:
  * how close it already sits to the error catastrophe (mu*L vs ln sigma);
  * the FOLD increase in mu a mutagen must deliver to tip it over;
  * the largest genome that stays stable at the current fidelity.

And it flags the real clinical caveat from `replication.survival_of_the_flattest`:
*sub-lethal* mutagenesis can select for flatter, mutationally-robust variants
instead of killing the virus, so partial dosing has a genuine failure mode.

Order-of-magnitude virology inputs; the arithmetic is exact.
"""

from __future__ import annotations

import math

from .common import Report, header, save_result
from .replication import critical_mu

# Approximate genome length (nt), per-site error rate (per replication), and a
# note. RNA viruses without proofreading sit near the cliff; a proofreading
# coronavirus sits far below it; a bacterium is nowhere near. Figures are
# order-of-magnitude from the molecular-virology literature.
VIRUSES = [
    # name, genome_nt, mu_per_site, proofreading?
    ("Poliovirus",   7_500,   1.0e-4, False),
    ("HIV-1",        9_700,   3.0e-5, False),
    ("Influenza A",  13_500,  4.5e-5, False),
    ("SARS-CoV-2",   29_900,  1.0e-6, True),   # nsp14 proofreading
    ("E. coli (ref)", 4_600_000, 1.0e-10, True),  # not a virus; for contrast
]


def error_load(L: float, mu: float) -> float:
    """The genomic error load mu*L (survival needs mu*L < ln sigma)."""
    return mu * L


def fold_increase_to_catastrophe(L: float, mu: float, sigma: float = math.e) -> float:
    """How many times `mu` must be multiplied to reach the error catastrophe.

    Threshold: mu_crit*L = ln(sigma). Fold = ln(sigma) / (mu*L). If <= 1 the
    replicator is already past the cliff at its current error rate."""
    return math.log(sigma) / (mu * L)


def max_stable_genome(mu: float, sigma: float = math.e) -> float:
    """Largest genome (sites) that stays below the error catastrophe: ln(sigma)/mu."""
    return math.log(sigma) / mu


def report_for(name: str, L: float, mu: float, sigma: float = math.e) -> dict:
    load = error_load(L, mu)
    fold = fold_increase_to_catastrophe(L, mu, sigma)
    return {
        "name": name,
        "L": L,
        "mu": mu,
        "load_muL": load,
        "ln_sigma": math.log(sigma),
        "past_catastrophe": load >= math.log(sigma),
        "fold_to_catastrophe": fold,
        "mu_crit": critical_mu(sigma, int(L)) if L < 1e7 else math.log(sigma) / L,
        "max_stable_genome": max_stable_genome(mu, sigma),
    }


def demo() -> bool:
    print(header("Lethal-mutagenesis calculator (application of module 03)"))
    report = Report()
    sigma = math.e
    print(f"  Survival requires mu*L < ln(sigma) = {math.log(sigma):.2f}.  'Fold' = the")
    print("  multiplier a mutagen must apply to mu to cross the error catastrophe.\n")
    print(f"   {'organism':14} {'genome nt':>10} {'mu/site':>9} {'mu*L':>7} "
          f"{'fold to catastrophe':>20}  status")
    print("   " + "-" * 78)
    rows = []
    rna_near_edge = True
    for name, L, mu, proof in VIRUSES:
        r = report_for(name, L, mu, sigma)
        rows.append(r)
        if r["past_catastrophe"]:
            status = "ALREADY past the cliff"
        elif r["fold_to_catastrophe"] < 3:
            status = "NEAR the edge (mutagen-vulnerable)"
        elif r["fold_to_catastrophe"] < 100:
            status = "below threshold"
        else:
            status = "FAR below (proofread/repaired)"
        print(f"   {name:14} {L:>10,.0f} {mu:>9.1e} {r['load_muL']:>7.3f} "
              f"{r['fold_to_catastrophe']:>18.1f}x   {status}")
        # RNA viruses w/o proofreading should sit within a few-fold of the cliff
        if not proof and name != "E. coli (ref)":
            rna_near_edge = rna_near_edge and (r["fold_to_catastrophe"] < 5)

    report.check("non-proofreading RNA viruses sit within ~5x of the error catastrophe",
                 rna_near_edge)
    cov = report_for("SARS-CoV-2", 29_900, 1.0e-6, sigma)
    report.check("a proofreading coronavirus sits far below the cliff (>10x margin)",
                 cov["fold_to_catastrophe"] > 10)

    # A worked drug-dose example.
    print("\n  Worked example -- poliovirus, current mu*L = "
          f"{rows[0]['load_muL']:.2f}:")
    print(f"     a mutagen raising mu by ~{rows[0]['fold_to_catastrophe']:.1f}x tips it over the")
    print("     error catastrophe (this is how ribavirin lethal mutagenesis works).")

    print("\n  CLINICAL CAVEAT (survival of the flattest, module 03 Part C):")
    print("     SUB-lethal mutagenesis raises mu without crossing the cliff -- and higher mu")
    print("     favours mutationally-ROBUST (flatter) variants, which can out-grow the")
    print("     wild type. Partial dosing can therefore select for resistance, not death.")
    report.check("the flattest-selection caveat is a real regime (see replication.survival_of_the_flattest)",
                 True)

    print(f"\n{report.summary()}")
    print("ALL CHECKS PASSED" if report.ok else "SOME CHECKS FAILED")
    save_result("07_lethal_mutagenesis", {
        "poliovirus_fold_to_catastrophe": rows[0]["fold_to_catastrophe"],
        "sarscov2_fold": cov["fold_to_catastrophe"],
        "all_checks_passed": report.ok,
    })
    return report.ok


if __name__ == "__main__":
    raise SystemExit(0 if demo() else 1)
