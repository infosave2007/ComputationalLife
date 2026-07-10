#!/usr/bin/env python3
"""Self-observation: the good regulator, and why a self-model must be lossy.

Good-regulator theorem (Conant & Ashby 1970):
    every good regulator of a system must be (contain) a model of that system.

Self-model corollary:
    if the target T an agent must predict *contains the agent's own model M*
    (plus the rest of the world E), then a b_M-bit model cannot be exact
    (2^{b_M} < |T|), and there is an irreducible floor on self-unpredictability
        H(T | M) >= H(T) - b_M                         (data-processing ineq.)

This module (1) states the analytic bounds, (2) demonstrates the DPI floor for
an ARBITRARY deterministic model g (not merely the best-case prefix model) via
random hashing, with bootstrap confidence intervals, across uniform, Zipf, and
Markov sources, and (3) actually DEMONSTRATES the good-regulator theorem on a
small finite system -- showing the optimal regulator is forced to be a model of
its disturbance, and that its required size is exactly the same b bits the
self-model floor demands.

Pure information theory + Monte-Carlo. No physics.
"""

from __future__ import annotations

import itertools
import math
from collections import defaultdict
from typing import Callable

import numpy as np

from .common import (
    Report,
    bootstrap_entropy_ci,
    entropy_from_samples,
    entropy_miller_madow,
    entropy_plugin,
    fmt_pow2,
    header,
    save_result,
)

# --------------------------------------------------------------------------- #
#  Part 1-4: analytic bounds
# --------------------------------------------------------------------------- #
PARAM_SETS = [
    dict(name="toy", B=256, b_M=6, logT=16, H=16, beta=4),
    dict(name="small", B=1024, b_M=10, logT=20, H=18, beta=8),
    dict(name="chip", B=8192, b_M=64, logT=128, H=128, beta=16),
    dict(name="cortex", B=10**6, b_M=1000, logT=2000, H=2000, beta=64),
    dict(name="giant", B=2**30, b_M=2**20, logT=2**40, H=2**40, beta=2**10),
]


def analyse(ps: dict[str, int]) -> dict[str, object]:
    """The four analytic quantities for one parameter set."""
    B, bM, logT, H, beta = ps["B"], ps["b_M"], ps["logT"], ps["H"], ps["beta"]
    return dict(
        deficit_bits=logT - bM,                 # log2|T| - b_M
        exact_possible=(bM >= logT),            # 2^{b_M} >= |T| ?
        Hcond_min=max(H - bM, 0),               # H(T|M) >= H(T) - b_M
        r=bM / logT,                            # necessary compression ratio
        r_lt_1=(bM / logT < 1.0),
        D_max=B // beta,                        # homunculus regress depth
    )


# --------------------------------------------------------------------------- #
#  Sources
# --------------------------------------------------------------------------- #
def uniform_source(H: int, n: int, rng: np.random.Generator) -> tuple[np.ndarray, int, float]:
    """Uniform over 2^H symbols. Returns (samples, support_size, true_entropy)."""
    k = 1 << H
    return rng.integers(0, k, size=n, dtype=np.int64), k, float(H)


def zipf_source(H: int, n: int, rng: np.random.Generator, s: float = 1.2
                ) -> tuple[np.ndarray, int, float]:
    """Zipf(s) over 2^H symbols. Returns (samples, support, exact entropy)."""
    k = 1 << H
    ranks = np.arange(1, k + 1)
    pmf = ranks ** (-s)
    pmf /= pmf.sum()
    samples = rng.choice(k, size=n, p=pmf)
    H_true = float(-np.sum(pmf * np.log2(pmf)))
    return samples.astype(np.int64), k, H_true


def markov_source(H: int, n: int, rng: np.random.Generator, seed_state: int = 0
                  ) -> tuple[np.ndarray, int, float]:
    """First-order Markov chain over 2^H symbols; return the *marginal* samples
    and the stationary marginal entropy (the quantity the b_M bound constrains).

    A sticky, non-uniform stationary law makes the prefix model non-optimal."""
    k = 1 << H
    # Sticky chain: stay with prob rho, else jump to a non-uniform target law.
    ranks = np.arange(1, k + 1)
    target = ranks ** (-1.1)
    target /= target.sum()
    rho = 0.7
    state = seed_state
    out = np.empty(n, dtype=np.int64)
    jumps = rng.random(n)
    dests = rng.choice(k, size=n, p=target)
    for i in range(n):
        if jumps[i] < rho:
            state = state  # stay
        else:
            state = int(dests[i])
        out[i] = state
    # stationary marginal == target (the jump law); its entropy:
    H_true = float(-np.sum(target * np.log2(target)))
    return out, k, H_true


# --------------------------------------------------------------------------- #
#  Models g: T -> M  (deterministic; H(T|M) = H(T) - H(M))
# --------------------------------------------------------------------------- #
def prefix_model(t: np.ndarray, b_M: int, H: int) -> np.ndarray:
    """Keep the top b_M bits. Entropy-optimal ONLY for a uniform source."""
    shift = max(H - b_M, 0)
    return (t >> shift).astype(np.int64)


def random_hash_model(t: np.ndarray, b_M: int, H: int, rng: np.random.Generator,
                      distinct_bits: int | None = None) -> tuple[np.ndarray, int]:
    """An ARBITRARY deterministic g: assign each target value a random bucket.

    This is the general case the DPI is really about. With ``distinct_bits < b_M``
    the model deliberately wastes capacity (fewer live buckets), so H(M) < b_M
    strictly and H(T|M) sits strictly above the floor -- a genuinely arbitrary g,
    unlike a contrived prefix construction.
    """
    k = 1 << H
    n_buckets = 1 << (distinct_bits if distinct_bits is not None else b_M)
    labels = rng.integers(0, n_buckets, size=k, dtype=np.int64)
    return labels[t], (1 << b_M)


def greedy_partition_model(t: np.ndarray, pmf: np.ndarray, b_M: int
                           ) -> tuple[np.ndarray, int]:
    """Strong heuristic for the entropy-optimal b_M-bit model: keep the
    2^{b_M}-1 most probable symbols as singletons, lump the rest into one
    'other' bucket. Not provably globally optimal, but it maximises retained
    variety far better than prefix truncation on skewed sources."""
    n_buckets = 1 << b_M
    order = np.argsort(pmf)[::-1]           # most probable first
    keep = order[: n_buckets - 1]
    label_of = np.full(pmf.size, n_buckets - 1, dtype=np.int64)  # default 'other'
    label_of[keep] = np.arange(n_buckets - 1)
    return label_of[t], n_buckets


# --------------------------------------------------------------------------- #
#  DPI demonstration for arbitrary g
# --------------------------------------------------------------------------- #
def dpi_check(t: np.ndarray, m: np.ndarray, km: int, H_true: float,
              b_M: int, estimator=entropy_miller_madow) -> dict[str, float]:
    """For deterministic M = g(T): estimate H(M) and H(T|M) = H(T) - H(M) and
    compare to the analytic floor H(T) - b_M. Returns the measured quantities."""
    H_M = entropy_from_samples(m, km, estimator)
    H_T_hat = estimator(np.bincount(t))
    H_cond = H_T_hat - H_M
    floor = H_true - b_M
    return {
        "H_M": H_M,
        "H_M_le_bM": H_M <= b_M + 1e-6,
        "H_cond": H_cond,
        "floor": floor,
        "gap": H_cond - floor,
        "above_floor": H_cond >= floor - 0.05,
    }


def demo_dpi_arbitrary_g(report: Report, H: int = 14, n: int = 2_000_000,
                         seed: int = 0) -> dict[str, object]:
    print("\n" + header("DPI floor for an ARBITRARY model g  (random hashing)", "-"))
    print(f"  uniform source, H(T) = {H} bits, n = {n:,} draws")
    print("  M = g(T) with g a RANDOM labelling into 2^b_M buckets (not the best-case")
    print("  prefix model). The bound rests on I(T;M) = H(M) <= b_M for ANY g.\n")
    rng = np.random.default_rng(seed)
    t, k, H_true = uniform_source(H, n, rng)

    print("   b_M   H(M)      floor=H-bM   H(T|M)=H-H(M)   gap>=0?   (random g)")
    print("   " + "-" * 64)
    all_ok = True
    reps = 8
    rows = []
    # keep 2^b_M well-sampled: n / 2^b_M >~ 30
    b_grid = [b for b in range(2, H + 1, 2) if n / (1 << b) >= 30]
    for b_M in b_grid:
        gaps = []
        HMs = []
        for r in range(reps):
            m, km = random_hash_model(t, b_M, H, np.random.default_rng(seed + 100 + r))
            res = dpi_check(t, m, km, H_true, b_M)
            gaps.append(res["gap"])
            HMs.append(res["H_M"])
            all_ok = all_ok and res["above_floor"] and res["H_M_le_bM"]
        min_gap = min(gaps)
        mean_HM = float(np.mean(HMs))
        rows.append({"b_M": b_M, "H_M": mean_HM, "min_gap": min_gap})
        print(f"   {b_M:>3d}   {mean_HM:<8.4f}  {H_true - b_M:<11.3f}  "
              f"{H_true - mean_HM:<13.4f}  min_gap={min_gap:+.4f}")
    report.check("H(M) <= b_M and H(T|M) >= floor for all random g (arbitrary g)", all_ok)

    # capacity-wasting g: strict slack above the floor
    print("\n  capacity-wasting g (only 2^(b_M-3) live buckets) => strict slack above floor:")
    b_M = 12
    m, km = random_hash_model(t, b_M, H, np.random.default_rng(seed + 7),
                              distinct_bits=b_M - 3)
    res = dpi_check(t, m, km, H_true, b_M)
    print(f"   b_M={b_M}: H(M)={res['H_M']:.4f} (<= {b_M}),  "
          f"H(T|M)={res['H_cond']:.4f}  floor={res['floor']:.3f}  gap=+{res['gap']:.3f}")
    report.check("wasteful arbitrary g sits strictly ABOVE the floor (>0.5 bit)",
                 res["gap"] > 0.5)
    return {"arbitrary_g_rows": rows, "wasteful_gap": res["gap"]}


def _bootstrap_conditional_ci(p_T: np.ndarray, bucket_of: np.ndarray, n: int,
                              km: int, *, B: int = 400, alpha: float = 0.05,
                              seed: int = 0) -> tuple[float, float, float]:
    """CI for H(T|M) = H(T) - H(M) with M = g(T) deterministic, via a JOINT
    bootstrap: resample T counts, then aggregate the SAME counts into buckets so
    H(T) and H(M) share their sampling fluctuation and the estimator bias cancels
    (the earlier version compared a biased Ĥ(M) to an exact H(T) and dipped below
    the floor by ~1e-5 -- an artifact, not a violation)."""
    rng = np.random.default_rng(seed)
    boot = np.empty(B)
    for b in range(B):
        tc = rng.multinomial(n, p_T)
        mc = np.bincount(bucket_of, weights=tc, minlength=km)
        boot[b] = entropy_miller_madow(tc) - entropy_miller_madow(mc)
    point = float(np.mean(boot))
    lo = float(np.percentile(boot, 100 * alpha / 2))
    hi = float(np.percentile(boot, 100 * (1 - alpha / 2)))
    return point, lo, hi


def demo_bootstrap_ci(report: Report, H: int = 12, n: int = 1_000_000,
                      seed: int = 0) -> dict[str, object]:
    print("\n" + header("Estimator quality + one-sided lower bound with CIs", "-"))
    from .common import entropy_grassberger  # local import keeps the header tidy

    # (1) Characterise the estimators against the KNOWN true entropy. The prefix
    # model on a uniform source sits EXACTLY on the floor, so it is the wrong
    # place for a one-sided test; it is the right place to measure estimator bias.
    rng = np.random.default_rng(seed)
    t, k, H_true = uniform_source(H, n, rng)
    counts_t = np.bincount(t, minlength=k)
    h_plugin = entropy_plugin(counts_t)
    h_mm = entropy_miller_madow(counts_t)
    h_gr = entropy_grassberger(counts_t)
    _, lo, hi = bootstrap_entropy_ci(counts_t, n, estimator=entropy_miller_madow,
                                     B=400, seed=seed)
    print(f"  uniform source, true H(T) = {H_true:.4f} bits, n = {n:,}, K = {k} cells:")
    print(f"     plug-in     = {h_plugin:.5f}   (bias {h_plugin - H_true:+.5f})")
    print(f"     Miller-Madow= {h_mm:.5f}   (bias {h_mm - H_true:+.5f})")
    print(f"     Grassberger = {h_gr:.5f}   (bias {h_gr - H_true:+.5f})")
    print(f"     MM 95% bootstrap CI half-width = {(hi - lo) / 2:.5f} bits")
    report.check("Miller-Madow estimate within 0.01 bit of true H(T)",
                 abs(h_mm - H_true) < 0.01)
    report.check("Grassberger no more biased than plug-in",
                 abs(h_gr - H_true) <= abs(h_plugin - H_true) + 1e-9)

    # (2) One-sided lower bound where there is genuine SLACK (capacity-wasting g):
    # here the floor is a strict lower bound and the CI sits comfortably above it.
    print("\n  one-sided test where the bound has slack (wasteful arbitrary g):")
    print("     b_M   floor    H(T|M) point   95% CI (lower, upper)   lower>floor?")
    p_T = counts_t.astype(np.float64) / counts_t.sum()
    all_slack = True
    for b_M in (6, 9, 12):
        # wasteful g: hash into only 2^(b_M-3) live buckets => strict slack.
        live = 1 << (b_M - 3)
        labels = np.random.default_rng(seed + b_M).integers(0, live, size=k)
        bucket_of = labels.astype(np.int64)
        cond_point, cond_lo, cond_hi = _bootstrap_conditional_ci(
            p_T, bucket_of, n, live, B=400, seed=seed + b_M)
        floor = H_true - b_M
        ok = cond_lo > floor
        all_slack = all_slack and ok
        print(f"     {b_M:>3d}   {floor:<7.2f}  {cond_point:<13.4f}  "
              f"({cond_lo:.4f}, {cond_hi:.4f})      {ok}")
    report.check("lower 95% CI strictly above floor when the bound has slack",
                 all_slack)
    return {"mm_bias": h_mm - H_true, "grassberger_bias": h_gr - H_true}


def demo_nonuniform_sources(report: Report, H: int = 12, n: int = 1_500_000,
                            seed: int = 0) -> dict[str, object]:
    print("\n" + header("Non-uniform & Markov sources: floor holds; 'optimal' isn't prefix", "-"))
    rng = np.random.default_rng(seed)
    sources = {
        "uniform": uniform_source(H, n, rng),
        "zipf": zipf_source(H, n, rng, s=1.2),
        "markov": markov_source(H, n, rng),
    }
    b_M = 6
    print(f"  b_M = {b_M};  comparing prefix / greedy / random g on each source.")
    print("  (floor = H(T) - b_M must hold for ALL; greedy should beat prefix on skew)\n")
    print(f"   {'source':8} {'H(T)':>7} {'floor':>7} {'prefix H(T|M)':>14} "
          f"{'greedy H(T|M)':>14} {'random H(T|M)':>14}")
    print("   " + "-" * 74)
    all_floor = True
    greedy_beats_prefix_on_skew = True
    for name, (t, k, H_true) in sources.items():
        pmf = np.bincount(t, minlength=k).astype(np.float64)
        pmf /= pmf.sum()
        floor = H_true - b_M

        m_pref = prefix_model(t, b_M, H)
        cond_pref = H_true - entropy_from_samples(m_pref, 1 << b_M)

        m_greedy, kg = greedy_partition_model(t, pmf, b_M)
        cond_greedy = H_true - entropy_from_samples(m_greedy, kg)

        m_rand, kr = random_hash_model(t, b_M, H, np.random.default_rng(seed + 3))
        cond_rand = H_true - entropy_from_samples(m_rand, kr)

        for c in (cond_pref, cond_greedy, cond_rand):
            all_floor = all_floor and (c >= floor - 0.05)
        if name in ("zipf", "markov"):
            greedy_beats_prefix_on_skew = greedy_beats_prefix_on_skew and (
                cond_greedy <= cond_pref + 1e-9)
        print(f"   {name:8} {H_true:>7.3f} {floor:>7.3f} {cond_pref:>14.4f} "
              f"{cond_greedy:>14.4f} {cond_rand:>14.4f}")
    report.check("floor H(T|M) >= H(T)-b_M holds for all models & sources", all_floor)
    report.check("greedy model leaves <= residual than prefix on skewed sources",
                 greedy_beats_prefix_on_skew)
    return {"nonuniform_floor_ok": all_floor}


# --------------------------------------------------------------------------- #
#  Conant-Ashby good-regulator theorem, actually demonstrated
# --------------------------------------------------------------------------- #
def _entropy_of_dist(prob: dict[int, float]) -> float:
    return float(-sum(p * math.log2(p) for p in prob.values() if p > 0))


def optimal_regulator(phi: Callable[[int, int], int], p_D: list[float], r: int
                      ) -> tuple[float, list[tuple[int, ...]]]:
    """Brute-force the good regulator: over all deterministic policies rho: D->R,
    find those minimising outcome entropy H(Z). Returns (min H(Z), argmin list)."""
    d = len(p_D)
    best_H = math.inf
    best: list[tuple[int, ...]] = []
    for policy in itertools.product(range(r), repeat=d):
        zdist: dict[int, float] = defaultdict(float)
        for di in range(d):
            zdist[phi(di, policy[di])] += p_D[di]
        Hz = _entropy_of_dist(zdist)
        if Hz < best_H - 1e-12:
            best_H, best = Hz, [policy]
        elif abs(Hz - best_H) <= 1e-12:
            best.append(policy)
    return best_H, best


def demo_conant_ashby(report: Report) -> dict[str, object]:
    print("\n" + header("Conant-Ashby good regulator, DEMONSTRATED (not just cited)", "-"))
    # System: outcome Z = (D + R) mod n. Goal of a good regulator: minimise H(Z).
    n = 6
    p_D = [1.0 / n] * n

    def phi(d: int, rr: int) -> int:
        return (d + rr) % n

    minH, optimal = optimal_regulator(phi, p_D, r=n)
    print(f"  System: Z = (D + R) mod {n};  disturbance D uniform on {n} states.")
    print(f"  Brute force over all {n}^{n} = {n**n} deterministic policies rho: D->R.")
    print(f"  min H(Z) achievable = {minH:.6f} bits;  #optimal policies = {len(optimal)}")
    report.check("perfect regulation achievable (min H(Z) == 0)", minH < 1e-9)
    report.check("exactly n optimal policies (unique up to goal relabeling)",
                 len(optimal) == n)

    # Every optimal policy is an affine MODEL of D: rho(D) = (c - D) mod n.
    is_model = True
    constants = set()
    for policy in optimal:
        cset = {(policy[di] + di) % n for di in range(n)}
        is_model = is_model and (len(cset) == 1)
        constants |= cset
    report.check("every optimal regulator is a model rho(D)=(c-D) mod n",
                 is_model and len(constants) == n)
    print("  => the ONLY good regulators are exact models of D (one per goal constant c).")

    # Bit budget: a regulator seeing only b bits of D cannot beat H(Z) = k - b.
    # This is the SAME data-processing floor as the self-model bound.
    print("\n  Bit-budget link to the self-model floor (n = 2^k, k = 3):")
    k = 3
    n2 = 1 << k
    p_D2 = [1.0 / n2] * n2

    def phi2(d: int, rr: int) -> int:
        return (d + rr) % n2

    print("     b (regulator bits)   best H(Z)   floor k-b   matches?")
    floor_ok = True
    for b in range(0, k + 1):
        # best b-bit regulator: observe top b bits of D, cancel them.
        shift = k - b
        # rho(D) = (- (top-b-bits of D, placed high)) mod n2
        zdist: dict[int, float] = defaultdict(float)
        for d in range(n2):
            obs = d >> shift            # b-bit view of D
            action = (-(obs << shift)) % n2
            zdist[phi2(d, action)] += p_D2[d]
        Hz = _entropy_of_dist(zdist)
        floor = k - b
        match = abs(Hz - floor) < 1e-9
        floor_ok = floor_ok and match
        print(f"     {b:>16d}   {Hz:>9.4f}   {floor:>9d}   {match}")
    report.check("b-bit regulator floor H(Z) = k - b (same DPI as self-model bound)",
                 floor_ok)
    print("  => a good regulator with b bits has residual variety H(Z) >= H(D) - b,")
    print("     the exact analogue of H(T|M) >= H(T) - b_M.  Regulation IS modelling.")
    return {"min_HZ": minH, "n_optimal_policies": len(optimal), "bit_floor_ok": floor_ok}


def multi_agent_residual(k: int, budgets: list[int]) -> float:
    """Several regulators of Z = (D + sum R_i) mod 2^k, each seeing a DISJOINT
    block of bits of D. Their capacities add: the residual variety is
    H(Z) = max(0, k - sum(budgets)). Returns the measured H(Z)."""
    n = 1 << k
    p_D = 1.0 / n
    # assign disjoint bit-blocks to agents until k bits are covered
    assigned = 0
    blocks = []
    for b in budgets:
        take = min(b, k - assigned)
        blocks.append((assigned, take))   # (start bit-from-top, width)
        assigned += take
    zdist: dict[int, float] = defaultdict(float)
    for d in range(n):
        action = 0
        for start, width in blocks:
            if width == 0:
                continue
            shift = k - start - width
            block_val = (d >> shift) & ((1 << width) - 1)
            action += (-(block_val << shift)) % n   # cancel this block
        zdist[(d + action) % n] += p_D
    return _entropy_of_dist(zdist)


def demo_multi_agent(report: Report) -> dict[str, object]:
    print("\n" + header("Multi-agent regulation: capacities add", "-"))
    print("  Z = (D + R1 + R2 + ...) mod 2^k, disturbance D on k=4 bits.")
    print("  Each regulator sees a disjoint slice of D; residual should be k - sum(budgets).\n")
    k = 4
    print("     budgets       sum b    measured H(Z)    floor max(0,k-sum)   match?")
    all_ok = True
    for budgets in ([1], [2, 1], [2, 2], [1, 1, 1], [3, 3]):
        hz = multi_agent_residual(k, budgets)
        floor = max(0, k - sum(budgets))
        ok = abs(hz - floor) < 1e-9
        all_ok = all_ok and ok
        print(f"     {str(budgets):13s} {sum(budgets):>4d}     {hz:>10.4f}       {floor:>10d}        {ok}")
    report.check("multi-agent residual H(Z) = max(0, k - sum budgets) (capacities add)",
                 all_ok)
    return {"multi_agent_ok": all_ok}


def demo_quantization(report: Report, C: int = 400, K: int = 16,
                      seed: int = 0) -> dict[str, object]:
    """Compressing a model's OWN parameters raises its prediction cost — the
    self-model bit-budget floor, applied to weights (the honest core of the
    'LLM quantization loses self-predictability' intuition)."""
    print("\n" + header("Compressing a model's weights raises its prediction cost", "-"))
    rng = np.random.default_rng(seed)
    logits = rng.normal(0, 2.5, size=(C, K))            # the 'model'
    ex = np.exp(logits - logits.max(axis=1, keepdims=True))
    true = ex / ex.sum(axis=1, keepdims=True)           # its true next-symbol dists
    base_H = float(np.mean(-np.sum(true * np.log2(true + 1e-30), axis=1)))
    print(f"  model over {C} contexts x {K} symbols; true prediction entropy = {base_H:.4f} bits")
    print("     weight bits/param   cross-entropy   excess over model's own entropy")
    prev_excess = -1.0
    monotone = True
    for qbits in (8, 5, 3, 2, 1):
        lo, hi = logits.min(), logits.max()
        step = (hi - lo) / (2 ** qbits - 1)
        q = lo + np.round((logits - lo) / step) * step   # uniform-quantized weights
        eq = np.exp(q - q.max(axis=1, keepdims=True))
        pred = eq / eq.sum(axis=1, keepdims=True)
        ce = float(np.mean(-np.sum(true * np.log2(pred + 1e-30), axis=1)))
        excess = ce - base_H
        if prev_excess >= 0 and excess < prev_excess - 1e-6:
            monotone = False
        prev_excess = excess
        print(f"     {qbits:>13d}      {ce:>10.4f}       +{excess:.4f}")
    report.check("coarser weights => higher prediction cost (excess grows as bits shrink)",
                 monotone and prev_excess > 0.0)
    print("  => fewer bits in the model = a lossier self-model = worse prediction:")
    print("     the H(T|M) >= H(T) - b_M floor, now applied to the model's own parameters.")
    return {"quantization_excess_1bit": prev_excess}


# --------------------------------------------------------------------------- #
#  Main
# --------------------------------------------------------------------------- #
def demo() -> bool:
    print(header("Self-observation: the good regulator & the lossy self-model"))
    report = Report()

    # ---- analytic bounds ----
    print("\n" + header("Analytic bounds (parts 1-4)", "-"))
    print(f"{'set':8} {'B':>12} {'b_M':>10} {'log2|T|':>10} {'H(T)':>8} "
          f"{'deficit':>9} {'2^bM<|T|':>9} {'H(T|M)>=':>10} {'r':>9} {'D<=B/b':>9}")
    for ps in PARAM_SETS:
        r = analyse(ps)
        print(f"{ps['name']:8} {ps['B']:>12} {ps['b_M']:>10} {ps['logT']:>10} "
              f"{str(ps['H']):>8} {str(r['deficit_bits']):>9} "
              f"{('YES' if not r['exact_possible'] else 'no'):>9} "
              f"{str(r['Hcond_min']):>10} {r['r']:>9.4g} {str(r['D_max']):>9}")
    all_impossible = all(not analyse(ps)["exact_possible"] for ps in PARAM_SETS)
    all_ratio_lt1 = all(analyse(ps)["r_lt_1"] for ps in PARAM_SETS)
    report.check("exact self-inclusive model impossible for every set (2^b_M < |T|)",
                 all_impossible)
    report.check("necessary compression ratio r < 1 for every set", all_ratio_lt1)
    print("   (|T| example, cortex:  " + fmt_pow2(2000) + ")")

    # ---- Monte-Carlo demonstrations ----
    res_dpi = demo_dpi_arbitrary_g(report)
    res_ci = demo_bootstrap_ci(report)
    res_nu = demo_nonuniform_sources(report)
    res_ca = demo_conant_ashby(report)
    res_ma = demo_multi_agent(report)
    res_q = demo_quantization(report)

    print("\n" + header("CONCLUSION"))
    print("A b_M-bit deterministic self-model leaves H(T|M) >= H(T) - b_M bits of")
    print("irreducible self-unpredictability -- demonstrated for ARBITRARY g (random")
    print("hashing) with bootstrap CIs, across uniform/Zipf/Markov sources. The")
    print("good-regulator theorem is demonstrated directly: the optimal regulator is")
    print("forced to be a model of its disturbance, and needs the same b bits.")
    print(f"\n{report.summary()}")
    print("ALL CHECKS PASSED" if report.ok else "SOME CHECKS FAILED")

    save_result("02_self_model", {
        "all_impossible": all_impossible,
        **res_dpi, **res_ci, **res_nu, **res_ca, **res_ma, **res_q,
        "all_checks_passed": report.ok,
    })
    return report.ok


if __name__ == "__main__":
    raise SystemExit(0 if demo() else 1)
