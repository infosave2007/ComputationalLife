#!/usr/bin/env python3
"""Self-reproduction: von Neumann's dual-use tape + Eigen's quasispecies.

PART A -- von Neumann's dual-use tape.
    An organism = (machinery + tape). The tape is used in TWO modes:
      (1) INTERPRETED by a constructor  -> rebuilds the machinery,
      (2) COPIED VERBATIM by a copier    -> handed to the offspring.
    We show child == parent (byte-identical), grandchild self-boots from the
    child's own bytes, a tape mutation is inherited verbatim, and the parent ->
    child map is a single payload-length-independent operator.

PART B -- Eigen's error threshold, done three ways of increasing rigour:
    B1. the 2-compartment closed form  x* = (sigma*(1-mu)^L - 1)/(sigma - 1);
    B2. the FULL quasispecies distribution as the Perron-Frobenius eigenvector
        of the exact Hamming-class-lumped mutation-selection matrix
        W = Q @ diag(f), validated against brute-force 2^L enumeration;
    B3. an exact finite-population Wright-Fisher survival curve.
    All three agree on the threshold  mu_crit * L -> ln(sigma)  as L grows, and
    B2 shows honestly that at finite L the master fraction is *smooth*, never a
    sharp zero -- the sharp catastrophe is the L->infinity / no-back-mutation
    limit.

No physics is used anywhere in this module.
"""

from __future__ import annotations

import math
from math import comb

import numpy as np

from .common import Report, header, save_result

# =========================================================================== #
# PART A -- von Neumann self-replicator (dual-use tape)
# =========================================================================== #
#
# Genome layout (a flat string = the whole organism):
#
#     <machinery source>  SEP1  <hex(machinery)>  SEP2  <payload>
#     \_________________/       \_____________________/\_________/
#          machinery M                    tape                phi
#
# SEP1/SEP2 are ASCII control chars that never occur in the machinery *source*
# (which writes chr(30)/chr(29), not the raw bytes), nor in hex digits or the
# alphabetic payload -- so parsing is unambiguous.

MACHINERY = (
    "def replicate(organism):\n"
    "    SEP1 = chr(30)  # machinery | tape\n"
    "    SEP2 = chr(29)  # machinery_hex | payload  (inside the tape)\n"
    "    machinery_src, tape = organism.split(SEP1, 1)\n"
    "    machinery_hex, payload = tape.split(SEP2, 1)\n"
    "    # (1) INTERPRET the tape: decode the description -> build the machinery\n"
    "    child_machinery = bytes.fromhex(machinery_hex).decode('utf-8')\n"
    "    # (2) COPY the tape verbatim -> hand it to the offspring (inert data)\n"
    "    child_tape = tape\n"
    "    return child_machinery + SEP1 + child_tape\n"
)

SEP1 = chr(30)
SEP2 = chr(29)


def build_organism(machinery_src: str, payload: str) -> str:
    """Assemble an organism whose tape truly describes its own machinery."""
    machinery_hex = machinery_src.encode("utf-8").hex()
    tape = machinery_hex + SEP2 + payload
    return machinery_src + SEP1 + tape


def replicate_via_own_machinery(organism: str) -> str:
    """Extract the machinery from the organism's OWN bytes, exec it, and use IT
    (not any top-level copy) to replicate -- proof the child is genuinely alive."""
    machinery_src = organism.split(SEP1, 1)[0]
    ns: dict[str, object] = {}
    exec(machinery_src, ns)  # noqa: S102 -- deliberate: booting the organism
    return ns["replicate"](organism)  # type: ignore[operator]


def hamming(a: str, b: str) -> int:
    if len(a) != len(b):
        raise ValueError("hamming distance needs equal-length strings")
    return sum(1 for x, y in zip(a, b) if x != y)


def mutate_payload(organism: str, payload_marker: str = "AAAAAAAA",
                   offset: int = 3, new_sym: str = "Z") -> tuple[str, int]:
    """Flip exactly one symbol inside the payload region; return (mutant, pos)."""
    chars = list(organism)
    tape_start = organism.index(SEP1) + 1
    payload_start = organism.index(SEP2, tape_start) + 1
    pos = payload_start + organism.index(payload_marker, payload_start) - payload_start + offset
    # locate marker relative to payload, then step `offset` into it
    pos = payload_start + (organism.index(payload_marker, payload_start) - payload_start) + offset
    if chars[pos] == new_sym:
        new_sym = "Q"
    chars[pos] = new_sym
    return "".join(chars), pos


def part_a(report: Report) -> dict[str, object]:
    print(header("PART A -- von Neumann dual-use tape: a self-reproducing automaton"))

    payload0 = "GENE_v1_AAAAAAAA"
    parent = build_organism(MACHINERY, payload0)

    ns: dict[str, object] = {}
    exec(MACHINERY, ns)  # noqa: S102
    replicate = ns["replicate"]  # type: ignore[assignment]

    child = replicate(parent)
    grandchild = replicate_via_own_machinery(child)

    tape = parent.split(SEP1, 1)[1]
    print("Organism layout : <machinery>  SEP1  <hex(machinery)>  SEP2  <payload>")
    print(f"Machinery bytes  : {len(MACHINERY.encode('utf-8')):>6d}")
    print(f"Tape length      : {len(tape):>6d} chars  ({len(tape.encode('utf-8')) * 8} bits)")
    print(f"Organism size    : {len(parent):>6d} chars  ({len(parent.encode('utf-8')) * 8} bits)")
    print("\nReplication faithfulness:")
    report.check("child == parent (byte-identical)", child == parent)
    report.check("grandchild == child (child booted from its OWN bytes)", grandchild == child)
    report.check("lineage stable (grandchild == parent)", grandchild == parent)

    # The parent->child map is ONE fixed operator, independent of payload length:
    parent_long = build_organism(MACHINERY, payload0 * 10)
    child_long = replicate(parent_long)
    mach_short = parent.split(SEP1, 1)[0]
    mach_long = parent_long.split(SEP1, 1)[0]
    print("\nConstant-size transition operator (the honest content of K(child) <= K(parent)+O(1)):")
    report.check("10x-longer payload still replicates faithfully", child_long == parent_long)
    report.check("machinery is identical for 1x and 10x payload", mach_short == mach_long)
    print(f"   replicate() is a fixed {len(MACHINERY.encode('utf-8'))}-byte operator; child == parent, so")
    print("   the transition is a payload-length-independent O(1) step (not a size claim about the identity).")

    # Open-ended heredity: mutate the tape; the COPY channel inherits it verbatim.
    mutant, mut_pos = mutate_payload(parent)
    print("\nOpen-ended heredity (one-symbol mutation on the tape):")
    report.check("d(mutant, parent) == 1", hamming(mutant, parent) == 1)
    mut_child = replicate(mutant)
    report.check("mut_child == mutant (inherited verbatim via COPY channel)", mut_child == mutant)
    report.check("d(mut_child, parent) == 1 (exactly the mutation)", hamming(mut_child, parent) == 1)
    mut_grandchild = replicate_via_own_machinery(mut_child)
    report.check("mutation survives to generation 2", mut_grandchild == mutant)
    print(f"   flipped one payload symbol at index {mut_pos}.")

    return {
        "machinery_bytes": len(MACHINERY.encode("utf-8")),
        "organism_bytes": len(parent.encode("utf-8")),
        "child_equals_parent": child == parent,
    }


# =========================================================================== #
# PART B1 -- Eigen 2-compartment closed form (corrected threshold solver)
# =========================================================================== #
def master_fraction_2c(mu: float, L: int, sigma: float) -> float:
    """Deterministic 2-compartment steady-state master fraction (closed form).

    x* = (sigma*(1-mu)^L - 1) / (sigma - 1) when positive, else 0. Using the
    exact fixed point (not a finite iteration) removes the near-threshold
    convergence bias that made an earlier version report mu_crit*L > 1.
    """
    Q = (1.0 - mu) ** L
    x = (sigma * Q - 1.0) / (sigma - 1.0)
    return x if x > 0.0 else 0.0


def critical_mu(sigma: float, L: int) -> float:
    """Exact per-genome error threshold: sigma*(1-mu)^L = 1  =>  mu = 1 - sigma^(-1/L)."""
    return 1.0 - sigma ** (-1.0 / L)


def critical_mu_numeric(sigma: float, L: int, tol: float = 1e-15) -> float:
    """Bisect the *exact existence condition* sigma*(1-mu)^L > 1.

    Because the survival test is analytic (not a decaying iterate), the located
    threshold now matches the closed form to machine precision and approaches
    ln(sigma) from below as L grows -- as the theory requires.
    """
    lo, hi = 0.0, 1.0
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        if sigma * (1.0 - mid) ** L > 1.0:  # master persists
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def finite_size_expansion(sigma: float, Ls: list[int]) -> list[dict[str, float]]:
    """Confirm mu_crit*L = ln(sigma) - (ln sigma)^2/(2L) + O(1/L^2), from below."""
    lns = math.log(sigma)
    rows = []
    for L in Ls:
        mc = critical_mu(sigma, L)
        muL = mc * L
        leading = lns
        second_order = lns - (lns**2) / (2.0 * L)
        rows.append({
            "L": L, "mu_crit": mc, "muL": muL,
            "ln_sigma": leading, "expansion_2nd": second_order,
            "err_vs_expansion": abs(muL - second_order),
        })
    return rows


# =========================================================================== #
# PART B2 -- full Eigen quasispecies via exact Hamming-class lumping
# =========================================================================== #
def _binom_pmf(m: int, p: float) -> np.ndarray:
    """pmf of Binomial(m, p) for k = 0..m, robust at p in {0, 1}."""
    if m == 0:
        return np.array([1.0])
    k = np.arange(m + 1)
    coef = np.array([comb(m, int(kk)) for kk in k], dtype=np.float64)
    if p <= 0.0:
        out = np.zeros(m + 1)
        out[0] = 1.0
        return out
    if p >= 1.0:
        out = np.zeros(m + 1)
        out[m] = 1.0
        return out
    return coef * (p ** k) * ((1.0 - p) ** (m - k))


def hamming_transition_matrix(L: int, mu: float) -> np.ndarray:
    """Exact (L+1)x(L+1) column-stochastic mutation kernel over Hamming classes.

    Q[i, j] = P(a sequence in error-class j mutates to class i). Exact lumping:
    from class j, the new class i = u + b where u ~ Binom(j, 1-mu) wrong bits
    that STAY wrong and b ~ Binom(L-j, mu) correct bits that FLIP -- so the
    column is the convolution of those two binomials. This includes
    back-mutation, unlike the 2-compartment cartoon.
    """
    Q = np.zeros((L + 1, L + 1))
    for j in range(L + 1):
        stay_wrong = _binom_pmf(j, 1.0 - mu)      # i contribution 0..j
        flip_correct = _binom_pmf(L - j, mu)      # i contribution 0..L-j
        Q[:, j] = np.convolve(stay_wrong, flip_correct)  # exactly length L+1
    return Q


def _perron(W: np.ndarray, iters: int = 200000, tol: float = 1e-15
            ) -> tuple[np.ndarray, float]:
    """Dominant (Perron-Frobenius) eigenpair of a nonnegative matrix by power
    iteration with L1 normalisation. For mu>0, W is strictly positive so the
    eigenvector is unique and nonnegative."""
    n = W.shape[0]
    v = np.full(n, 1.0 / n)
    lam = 0.0
    for _ in range(iters):
        w = W @ v
        lam = w.sum()
        w = w / lam
        if np.max(np.abs(w - v)) < tol:
            v = w
            break
        v = w
    return v, float(lam)


def quasispecies_distribution(sigma: float, L: int, mu: float
                              ) -> tuple[np.ndarray, float]:
    """Exact quasispecies distribution over error classes (single-peak landscape).

    Returns (p, mean_fitness) where p[k] is the stationary fraction in class k
    and p[0] is the master fraction. The operator is the standard Eigen
    reproduce-then-mutate matrix W[i,j] = Q[i,j] * f[j]."""
    Q = hamming_transition_matrix(L, mu)
    f = np.ones(L + 1)
    f[0] = sigma
    W = Q @ np.diag(f)
    p, lam = _perron(W)
    return p, lam


def quasispecies_bruteforce(sigma: float, L: int, mu: float) -> np.ndarray:
    """Reference: full 2^L quasispecies, aggregated to classes. For small L only.

    Uses the identical reproduce-then-mutate semantics as the lumped model, so
    agreement to ~1e-12 certifies the lumping is exact, not merely close."""
    n = 1 << L
    classes = np.array([bin(x).count("1") for x in range(n)])
    f = np.where(classes == 0, sigma, 1.0).astype(np.float64)
    # P(x -> y) = mu^d (1-mu)^(L-d), d = popcount(x ^ y).
    W = np.empty((n, n))
    for x in range(n):
        for y in range(n):
            d = bin(x ^ y).count("1")
            W[y, x] = (mu ** d) * ((1.0 - mu) ** (L - d))
        W[:, x] *= f[x]
    v, _ = _perron(W)
    p = np.zeros(L + 1)
    for x in range(n):
        p[classes[x]] += v[x]
    return p


def quasispecies_critical_mu(sigma: float, L: int, level: float = 0.01,
                             hi: float = 0.5) -> float:
    """Locate where the *full-model* master fraction p[0] drops through `level`.

    Because p[0] is smooth (back-mutation keeps it strictly positive), the
    'threshold' is defined operationally at a small level; it converges to the
    deterministic 1 - sigma^(-1/L) as L grows."""
    lo, hi_ = 0.0, hi
    for _ in range(60):
        mid = 0.5 * (lo + hi_)
        p, _ = quasispecies_distribution(sigma, L, mid)
        if p[0] > level:
            lo = mid
        else:
            hi_ = mid
    return 0.5 * (lo + hi_)


# =========================================================================== #
# PART B3 -- exact finite-population Wright-Fisher
# =========================================================================== #
def wf_master_fraction(mu: float, L: int, sigma: float, N: int, gens: int,
                       seed: int) -> float:
    """One exact Wright-Fisher run; returns master fraction after `gens` gens.

    Offspring counts are sampled with exact numpy binomial draws (no Gaussian
    approximation, no rare log(0) crash)."""
    rng = np.random.default_rng(seed)
    Q = (1.0 - mu) ** L
    m = N // 2
    for _ in range(gens):
        c = N - m
        wm = sigma * m
        w_total = wm + c
        p_master = (wm * Q) / w_total
        m = int(rng.binomial(N, p_master))
        if m == 0:
            break
    return m / N


def wf_survival_curve(mu: float, L: int, sigma: float, N: int, gens: int,
                      reps: int, seed: int = 0) -> tuple[float, float, float]:
    """Return (P_survive, mean_fraction, std_fraction) over `reps` replicates."""
    fracs = np.array([
        wf_master_fraction(mu, L, sigma, N, gens, seed=seed + r) for r in range(reps)
    ])
    p_survive = float(np.mean(fracs > 0.0))
    return p_survive, float(fracs.mean()), float(fracs.std())


# =========================================================================== #
# PART B -- demo
# =========================================================================== #
def part_b(report: Report) -> dict[str, object]:
    print("\n" + header("PART B -- Eigen quasispecies error threshold"))
    sigma = math.e
    L = 100
    print(f"Single-peak landscape: master fitness sigma = e = {sigma:.6f}, genome length L = {L}")

    # -- B1: 2-compartment closed form, corrected solver ---------------------
    print("\nB1. 2-compartment closed form  x* = (sigma*(1-mu)^L - 1)/(sigma-1):")
    print("   mu*L   Q=(1-mu)^L   sigma*Q   master x*   status")
    print("   " + "-" * 58)
    frac_below = frac_above = None
    for muL in [0.25, 0.5, 0.75, 0.9, 1.0, 1.1, 1.5, 2.0]:
        mu = muL / L
        Q = (1.0 - mu) ** L
        x = master_fraction_2c(mu, L, sigma)
        status = "survives" if x > 1e-9 else "COLLAPSE"
        print(f"   {muL:<5.2f}  {Q:<11.6f}  {sigma * Q:<8.5f}  {x:<10.6f}  {status}")
        if abs(muL - 0.5) < 1e-9:
            frac_below = x
        if abs(muL - 2.0) < 1e-9:
            frac_above = x
    report.check("master survives at mu*L = 0.5", bool(frac_below and frac_below > 0))
    report.check("master collapses at mu*L = 2.0", frac_above == 0.0)

    # corrected threshold now approaches ln(sigma) strictly FROM BELOW
    print("\n   corrected threshold solver (was biased high before the fix):")
    print("     L     mu_crit*L   ln(sigma)   from below?")
    ok_below = True
    for Lx in [50, 100, 500, 1000, 5000]:
        mc = critical_mu_numeric(sigma, Lx)
        muL = mc * Lx
        below = muL < math.log(sigma)
        ok_below = ok_below and below
        # numeric solver must match the closed form
        report.check(f"L={Lx}: numeric == closed-form mu_crit",
                     abs(mc - critical_mu(sigma, Lx)) < 1e-9, verbose=False)
        print(f"   {Lx:>6d}   {muL:<10.7f}  {math.log(sigma):<10.7f}  {below}")
    report.check("mu_crit*L < ln(sigma) for all L (approaches from below)", ok_below)

    exp_rows = finite_size_expansion(sigma, [50, 100, 500, 1000, 5000])
    max_exp_err = max(r["err_vs_expansion"] for r in exp_rows)
    report.check("finite-size 2nd-order expansion accurate (<1e-4)", max_exp_err < 1e-4)

    # -- B2: full quasispecies eigenvector, validated by brute force ---------
    print("\nB2. FULL Eigen quasispecies = Perron-Frobenius eigenvector of W = Q @ diag(f)")
    print("    (exact Hamming-class lumping, validated against 2^L enumeration):")
    print("     L    mu      lumped p[0]   bruteforce p[0]   |diff|")
    max_lump_err = 0.0
    for (Ls, mus) in [(6, 0.05), (8, 0.05), (10, 0.08)]:
        p_lump, _ = quasispecies_distribution(sigma, Ls, mus)
        p_bf = quasispecies_bruteforce(sigma, Ls, mus)
        diff = float(np.max(np.abs(p_lump - p_bf)))
        max_lump_err = max(max_lump_err, diff)
        print(f"   {Ls:>4d}  {mus:<6.3f}  {p_lump[0]:<12.9f}  {p_bf[0]:<15.9f}  {diff:.2e}")
    report.check("lumped quasispecies == brute-force 2^L enumeration (<1e-10)",
                 max_lump_err < 1e-10)

    # smoothness + positivity: master fraction never hits an exact zero at finite L
    print("\n    full model is SMOOTH at finite L (master fraction > 0 even past the")
    print("    2-compartment 'catastrophe') -- the sharp threshold is the L->inf limit:")
    Lq = 40
    print(f"     L = {Lq};   mu*L      2-compartment x*     full-model p[0]")
    all_positive = True
    for muL in [0.5, 1.0, 1.5, 2.0]:
        mu = muL / Lq
        x2c = master_fraction_2c(mu, Lq, sigma)
        pfull, _ = quasispecies_distribution(sigma, Lq, mu)
        all_positive = all_positive and (pfull[0] > 0)
        print(f"              {muL:<8.2f}  {x2c:<18.6f}   {pfull[0]:.6e}")
    report.check("full-model p[0] > 0 at finite L for all mu (smooth, no exact zero)",
                 all_positive)

    # full-model operational threshold converges to the deterministic one
    print("\n    full-model operational threshold (p[0] through 1%) -> deterministic:")
    print("     L     full mu_crit*L    deterministic mu_crit*L")
    conv = []
    for Lx in [20, 40, 80]:
        mc_full = quasispecies_critical_mu(sigma, Lx, level=0.01) * Lx
        mc_det = critical_mu(sigma, Lx) * Lx
        conv.append(abs(mc_full - mc_det))
        print(f"   {Lx:>6d}   {mc_full:<15.6f}   {mc_det:.6f}")
    report.check("full-model threshold converges toward deterministic as L grows",
                 conv[-1] < conv[0])

    # -- B3: exact finite-N Wright-Fisher ------------------------------------
    print("\nB3. exact finite-population Wright-Fisher (numpy binomial, mean +/- std over seeds):")
    p_lo, mean_lo, std_lo = wf_survival_curve(0.5 / L, L, sigma, N=200_000,
                                              gens=400, reps=16, seed=0)
    p_hi, mean_hi, std_hi = wf_survival_curve(2.0 / L, L, sigma, N=200_000,
                                              gens=400, reps=16, seed=0)
    print(f"   mu*L=0.5 -> P(survive)={p_lo:.3f}, master fraction={mean_lo:.4f} +/- {std_lo:.4f}  (persists)")
    print(f"   mu*L=2.0 -> P(survive)={p_hi:.3f}, master fraction={mean_hi:.4f} +/- {std_hi:.4f}  (collapsed)")
    report.check("WF: master persists below threshold (mean > 0.05)", mean_lo > 0.05)
    report.check("WF: master collapses above threshold (mean < 0.01)", mean_hi < 0.01)

    return {
        "sigma": sigma,
        "critical_muL_L100": critical_mu(sigma, 100) * 100,
        "lumped_vs_bruteforce_max_err": max_lump_err,
        "wf_master_fraction_muL_0p5": mean_lo,
    }


# =========================================================================== #
def demo() -> bool:
    print(header("Self-reproduction: von Neumann's tape + Eigen's error threshold"))
    report = Report()
    res_a = part_a(report)
    res_b = part_b(report)

    print("\n" + header("SUMMARY"))
    print("A) Dual-use tape (interpret + verbatim copy) => byte-exact, self-booting,")
    print("   mutation-heritable self-reproduction; parent->child is an O(1) operator.")
    print("B) Eigen threshold mu_crit*L -> ln(sigma), shown three ways (closed form,")
    print("   exact quasispecies eigenvector vs 2^L brute force, and finite-N WF).")
    print(f"\n{report.summary()}")
    print("ALL CHECKS PASSED" if report.ok else "SOME CHECKS FAILED")

    save_result("03_replication", {**res_a, **res_b, "all_checks_passed": report.ok})
    return report.ok


if __name__ == "__main__":
    raise SystemExit(0 if demo() else 1)
