# Computational Life

[![CI](https://github.com/infosave2007/ComputationalLife/actions/workflows/ci.yml/badge.svg)](.github/workflows/ci.yml)
![python](https://img.shields.io/badge/python-3.9%2B-blue)
![license](https://img.shields.io/badge/license-MIT-green)

🇷🇺 Русская версия: [README.ru.md](README.ru.md)

**One idea, made rigorous:** self-reproduction, self-observation, and self-modification
are not metaphors — they are classical theorems, and together with universal
computation and universal prediction they form a single **computational theory of life
and mind**. Every headline claim here is *implemented, run, self-verified by assertions,
and covered by an independent test*. No physics is used or needed; the one honest contact
point with NVG physics is a *boundary* (resource ceilings), documented in
[`NVG_INTERFACE.md`](NVG_INTERFACE.md). Each claim maps to the exact function and test
that backs it in [`CLAIMS.md`](CLAIMS.md).

## The unifying picture

| Layer | Who | What | Module |
|---|---|---|---|
| self-reproduction | **von Neumann** (1948) | constructor + dual-use description tape | [`replication`](complife/replication.py) |
| universal computation | **Turing** (1936) | one machine computes everything computable | (substrate) |
| self-reference | **Kleene** recursion thm | a program can read *and rewrite* its own code | [`self_reference`](complife/self_reference.py) |
| self-observation | **Conant–Ashby** (1970) | a good regulator must *model* its system | [`self_model`](complife/self_model.py) |
| prediction = compression | **Solomonoff / Hutter** | the best model is the shortest program | [`self_model`](complife/self_model.py), [`physical_limits`](complife/physical_limits.py) |

The recurring architecture is **"a cheap program + a powerful shared decoder"**:
complexity lives in the decoder and the inputs, not in the program. That is what a data
compressor is (model + coder), what a genome is (recipe + physics/chemistry), and what an
agent's self-model is (a compressed predictor of itself).

## The four modules

### `self_reference` — self-reference is real, *general*, and cheap
- A verified Python **quine** (stdout == source, byte-for-byte): **75 bytes**; plus verified
  toy-language quines (**Underload `(:aSS):aSS`**, 10 symbols; minimal-Lisp λ-quine, 99 bytes).
- The **second recursion theorem, constructively**: programs whose output is a *nontrivial
  function of their own source* — `sha256`, `length`, `reverse`, `upper` — each verified in a
  subprocess. Plus a **self-modifying** program that emits a copy of itself with an incremented
  counter and every other byte invariant. This is the "read *and rewrite* its own code" claim,
  now demonstrated rather than asserted.
- **Additive-constant overhead, two honest ways:** the repr-inlining construction has overhead
  measured to be exactly **159 + (#escaped chars)** — i.e. `O(#escapes)`, constant only for
  escape-free payloads; a **content-agnostic** construction (payload + fixed self-reading tail)
  has overhead **exactly constant (76 bytes)** for *arbitrary* payload bytes, including
  quotes/backslashes/newlines/random bytes.

### `self_model` — a self-model *must* be a lossy compression
- Exact self-inclusive modeling is **impossible** (`2^{b_M} < |T|` whenever the target contains
  the model plus anything else) — verified across 5 regimes.
- The self-unpredictability floor **`H(T|M) ≥ H(T) − b_M`** is demonstrated for an **arbitrary
  deterministic model `g`** (random hashing into `2^{b_M}` buckets), not merely the best-case
  prefix model — the bound reduces to `I(T;M) = H(M) ≤ b_M`, which we measure directly, with
  **bootstrap confidence intervals** and across **uniform, Zipf, and Markov** sources. A
  capacity-wasting `g` sits strictly above the floor (a genuine lower bound).
- The **Conant–Ashby good-regulator theorem is demonstrated**, not just cited: brute force over
  all deterministic policies shows the optimal regulator of `Z = (D+R) mod n` is *forced* to be
  a model `ρ(D) = (c − D) mod n` (unique up to the goal constant), and a `b`-bit regulator has
  residual variety **`H(Z) = H(D) − b`** — the exact analogue of the self-model floor.

### `replication` — small self-developing copies, with a limit
- **Dual-use tape:** an organism = machinery + tape, used two ways — *interpreted* to build the
  machinery, *copied verbatim* to the offspring. `child == parent` (byte-identical),
  `grandchild == child` (the child self-boots from its own bytes), a payload mutation is
  **inherited verbatim**; the parent→child map is a payload-length-independent `O(1)` operator.
- **Eigen error threshold, three ways:** the 2-compartment closed form; the **full quasispecies
  distribution** as the Perron–Frobenius eigenvector of the exact Hamming-class-lumped
  mutation–selection matrix `W = Q·diag(f)` — **validated against brute-force `2^L` enumeration
  to `~10⁻¹⁶`**; and an exact finite-population Wright–Fisher run. All agree that
  **`μ_crit·L → ln σ`** (approached *from below* as `L` grows). Honestly: with back-mutation the
  master fraction is *smooth* and strictly positive at finite `L` — the sharp catastrophe is the
  `L → ∞` limit.

### `physical_limits` — the only place physics enters
- **Storage:** Landauer `kB·T·ln2` = **2.87×10⁻²¹ J** at 300 K; a brain uses **~10⁻²⁷·⁶** of its
  Bekenstein ceiling — life is information-*sparse* (shown across E. coli → datacenter rack).
- **Speed (now computed, not just cited):** Margolus–Levitin `4E/h` ≈ **7.6×10⁵⁰ ops/s** for a
  brain; Bremermann `c²/h` ≈ **1.36×10⁵⁰ ops/s/kg**; Lloyd's ultimate laptop **5.4×10⁵⁰ ops/s**.
- **Throughput:** at the brain's ~20 W / 310 K budget, Landauer allows **6.7×10²¹** irreversible
  erasures/s — the brain runs ~7 orders of magnitude *above* the per-bit thermodynamic minimum
  (sparse in bits, profligate in energy/bit).
- **NVG interface (model-dependent, clearly flagged):** with the NVG *inputs* `M_Ω = 859 MeV`
  and "the vacuum melts at `ρ_c = M_Ω⁴/(ℏc)³` = 1.26×10²⁰ kg/m³", the extremal regular core has
  inner de Sitter scale `l = 1.128 km` and — the corrected geometry — an extremal horizon at
  `r_h = √3·l = 1.954 km` whose Bekenstein–Hawking entropy is **6.6×10⁷⁶ bits** (the inner-scale
  area bound `S(l) = 2.2×10⁷⁶` is a *different* quantity). Physics caps the container; it does
  not supply the computation.

## Install & run

```bash
pip install -e .            # or: pip install -r requirements.txt
python -m complife          # run all four modules, print a master PASS/FAIL summary
python -m complife 01 03    # run only the named modules
```

The four numbered scripts still work from the repo root and forward to the package:

```bash
python3 01_self_reference_quine.py   #  ==  python -m complife.self_reference
```

## Test

```bash
make test        # full suite (subprocess quines + Monte-Carlo), ~8 s
make test-fast   # skip the slow Monte-Carlo / subprocess tests
make cov         # coverage report
make lint        # ruff
```

Every scientific claim above is an independent `pytest` test (see [`CLAIMS.md`](CLAIMS.md)), not
just an in-demo assertion. Headline numbers are snapshotted to [`results/`](results/) on each run.

## Project layout

```
complife/            importable, tested package
  common.py          entropy estimators, bootstrap CIs, constants, reporting
  self_reference.py  quines, 2nd recursion theorem, additive-constant overhead
  self_model.py      DPI floor for arbitrary g, sources, Conant–Ashby regulator
  replication.py     dual-use tape, full Eigen quasispecies eigenvector, WF
  physical_limits.py storage/speed/throughput ceilings, NVG geometry
  __main__.py        `python -m complife`
tests/               one file per module + common + smoke + snapshots (51 tests)
01..04_*.py          thin runnable shims (preserve the original entry points)
CLAIMS.md            every claim -> function -> test -> caveat
NVG_INTERFACE.md     the one honest physics boundary (and the category errors)
```

Standard library + **numpy**. Deterministic (stochastic parts use fixed seeds).

## Honesty notes

- This is standard **algorithmic information theory + cybernetics** (Kleene, Conant–Ashby,
  von Neumann, Eigen, Solomonoff/Hutter). Nothing here beats Shannon; nothing here needs new physics.
- **Consciousness is *not* derived here.** "A self-modifying, self-observing program = self-awareness"
  is the unproven hard-problem bridge (Chalmers); self-reference is *necessary-ish* for self-modeling
  but is syntactic — it does not, by any proof, entail phenomenal experience.
- The relationship to NVG physics is a **boundary, not a merger** — see [`NVG_INTERFACE.md`](NVG_INTERFACE.md).
  The NVG numbers rest on asserted model inputs (the 859 MeV scale, the melting mechanism) and are
  labeled as such; the Landauer/Bekenstein/holographic/speed ceilings are first-principles.
