# Changelog

## 0.3.0 — two new walls, two extended bridges

Extended the project beyond the original four modules, keeping the "proven, not
asserted" rule. 72 tests, all green; ruff clean.

### New modules
- **`quantum`** — the fifth impossibility: an unknown quantum state **cannot be
  copied** (no-cloning), shown two independent ways in pure numpy (linearity turns
  a copy attempt into a Bell state; unitarity forbids it for non-orthogonal states),
  contrasted with the cheap *classical* copying that makes module 03 possible.
- **`induction`** — **prediction = compression** (Solomonoff / MDL): a
  shortest-program search recovers an LCG generator from a handful of samples and
  compresses its "random-looking" stream ~1000× (32 000 bits → a 32-bit program),
  while correctly failing on truly
  random data (no codec beats Shannon). No LLM, fully deterministic; honest that
  true Solomonoff induction is uncomputable.

### Extended modules
- **`replication`** — arbitrary **fitness landscapes** via `quasispecies_landscape`,
  demonstrating **survival of the flattest**: past a crossover mutation rate a
  shorter, wider peak out-grows a taller, narrower one.
- **`physical_limits`** — **LLM inference vs the Landauer floor**: a 70B model
  serves at ~10⁸× the thermodynamic minimum (~7.5 nJ/token floor), the same
  sparseness lesson as the brain, now for a datacenter GPU.
- **`self_model`** — **multi-agent regulation** (regulator capacities add:
  `H(Z) = max(0, k − Σbᵢ)`) and a **weight-quantization** demo (compressing a
  model's parameters raises its prediction cost — the `H(T|M)` floor for weights).
- **`self_reference`** — **Rice's theorem** constructively: every candidate decider
  of a non-trivial semantic property is refuted by its own diagonal program.

### On a proposed NVG addition (declined as stated, done honestly instead)
A suggestion to add a module "testing `ρ_c` / `M_crit` as numerical predictions" was
**not** implemented in that form: those quantities are *asserted NVG model inputs*
(the 859 MeV scale + melt mechanism), not first-principles predictions, and framing
them as validated predictions would be the exact category error `NVG_INTERFACE.md`
exists to prevent. What is honest — and already present — is the **internal
geometric-consistency** check (`test_nvg_core_geometry_consistent`); that is the
ceiling of what can be claimed.

### Deferred
- A verified Brainfuck quine (needs a published quine matching this interpreter's
  exact cell/EOF convention) — the interpreter is tested via Hello-World; the quine
  is cited, not run.

## 0.2.0 — rigor & packaging pass

Turned four self-contained scripts into a tested, packaged project, and upgraded every
module's calculations from best-case demonstrations to general ones. Guided by an
independent multi-agent audit (see `CLAIMS.md` for the resulting claim→test map).

### Fixed (confirmed defects)
- **`replication`**: the error-threshold solver used a fixed 20 000-iteration fixed-point
  map that does not converge near criticality, reporting `μ_crit·L > 1` (e.g. 1.00054 at
  L=5000) and contradicting the "approaches ln σ from below" claim. Replaced with the exact
  existence condition / closed form; the threshold now approaches `ln σ` from below to
  machine precision.
- **`replication`**: the "exact Wright–Fisher" check silently used a Gaussian approximation
  every generation and had a rare `log(0)` crash. Replaced with exact `numpy.random.binomial`;
  results are now reported as mean ± std over seeds.

### Added (higher-quality calculations)
- **`self_reference`**: constructive **second recursion theorem** (output = `g(own source)`
  for `g ∈ {sha256, length, reverse, upper}`), a **self-modifying** program, and a
  **content-agnostic** additive-constant construction whose overhead is exactly constant for
  arbitrary payload bytes (the repr construction is honestly characterized as `159 + #escapes`).
- **`self_model`**: the `H(T|M) ≥ H(T) − b_M` floor is now demonstrated for an **arbitrary**
  deterministic `g` (random hashing) with **bootstrap confidence intervals**, across
  **uniform / Zipf / Markov** sources; a greedy quantizer beats prefix truncation on skew; and
  the **Conant–Ashby good-regulator theorem is demonstrated** (brute-force optimal regulator is
  forced to be a model; a `b`-bit regulator has residual `H(Z) = H(D) − b`).
- **`replication`**: the **full Eigen quasispecies** as the Perron–Frobenius eigenvector of the
  exact Hamming-class-lumped matrix `W = Q·diag(f)`, validated against brute-force `2^L`
  enumeration (`~10⁻¹⁶`), with an explicit smooth-vs-sharp honesty note and a σ-sweep.
- **`physical_limits`**: computed **speed ceilings** (Margolus–Levitin, Bremermann, Lloyd),
  **Landauer throughput** at the brain's 20 W budget, and a **sparseness scan** across scales.
  Corrected the NVG geometry to separate the inner de Sitter scale (`S(l)=2.2×10⁷⁶`) from the
  extremal horizon (`r_h=√3·l`, `S_BH=6.6×10⁷⁶`); flagged the 859 MeV scale as a model input.

### Engineering
- `complife/` importable package with `common.py` (entropy estimators, bootstrap CIs, constants,
  a self-verifying `Report` harness, JSON result snapshots) and a `python -m complife` entry point.
- 51-test `pytest` suite (fast unit tests + `@slow` Monte-Carlo/subprocess), `results/` snapshots.
- `pyproject.toml`, `requirements*.txt`, `Makefile`, GitHub Actions CI (Python 3.9/3.11/3.12),
  ruff lint, MIT `LICENSE`, `CLAIMS.md`, this changelog. Numbered scripts kept as thin shims.

## 0.1.0 — initial
Four standalone scripts (self-reference, self-model, replication, physical limits) with inline
assertions and an NVG interface note.
