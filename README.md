# Computational Life

[![CI](https://github.com/infosave2007/ComputationalLife/actions/workflows/ci.yml/badge.svg)](.github/workflows/ci.yml)
![python](https://img.shields.io/badge/python-3.9%2B-blue)
![license](https://img.shields.io/badge/license-MIT-green)

🇷🇺 Русская версия: [README.ru.md](README.ru.md)

**Can a computer program copy itself, know itself, and rewrite itself — the same tricks that make you alive and awake?** This project says yes to some of it and a firm no to the rest, and it proves which is which with tiny programs you can run in seconds and watch pass or fail.

Here's the thing. People say a lot of huge stuff about life and minds: "the brain is a computer," "the universe is a simulation," "compression is intelligence." Most of it sounds cool but means nothing you can check. This repo takes a handful of those big ideas and turns each one into a short program that either works or doesn't when you press run. No arguing — just run it and see.

It is **not** a product or a tool that does a job for you. What it gives you is understanding you can trust.

## The questions it answers — with running code

Real questions, with real yes/no answers you can reproduce on your own laptop:

- **Can a program really print its own source code — or edit itself?** Yes. There's a **75-character** program here that prints itself, and another that rewrites itself while it runs.
- **Could you ever perfectly predict your own next move?** No — and there's an exact math floor on how much of yourself must stay a surprise. (Weird bonus: this is the *same* rule as "to steer something, you have to model it.")
- **Why can't a self-copying thing carry unlimited information?** Because if copying makes too many mistakes, the message turns to noise. There's a hard cliff. It's why viruses can't have giant genomes.
- **What are the speed and memory limits of *any* computer, and how close is a brain?** Nowhere close. A brain uses about a **trillionth of a trillionth** of its storage ceiling.

And it's honest about the edges: the one place it leans on far-out physics is fenced off and labeled, never sneaked in as fact.

## Why does this exist?

Two reasons.

**First, to build one honest foundation.** Instead of a hundred hand-wavy blog posts about "life as computation," this shows a single picture where copying yourself, modeling yourself, referring to yourself, predicting yourself, and the physics limits are all the *same* idea — and each piece is proven, not asserted.

**Second, as a reality check and a way to learn.** It's a place where grand claims about minds and machines either get grounded in code or get thrown out. Anyone can rerun the check.

## The one idea behind all of it

Look closely at anything alive or intelligent and you keep spotting the **same design**: a small set of instructions plus a powerful machine that unfolds them.

- A **zip file** is a few kilobytes plus an unzipper that rebuilds the whole thing.
- A **genome** is a recipe plus the chemistry that grows it into an animal.
- Your **sense of self** is a tiny compressed model plus a brain that runs it.

The recipe is cheap. The power lives in the thing that decodes it. This project makes that idea exact — and shows where each version of it **slams into a wall it can never get past**.

## The four parts

Each part starts in plain words. The precise math is folded into a "for the curious" box you can open if you want it.

### 1. A thing can refer to itself — [`self_reference`](complife/self_reference.py)

**In plain words:** A program can print its own source code, exactly — that's called a "quine," like a sentence that perfectly describes itself. The smallest one here is **75 characters**. It can go further: figure out *anything about itself*, and even **rewrite itself**. That's the math behind self-copying code. The catch: a system can point at itself forever but can **never fully "understand" itself** — that's Gödel's famous limit.

<details><summary>The precise version (for the curious)</summary>

**Kleene's recursion theorem.** Self-reference exists in every general-purpose language, and adding
"also reproduce yourself" to any program costs only a fixed number of bytes (shown exactly: a
constant 76-byte overhead for arbitrary content). We also build the **second recursion theorem**
constructively — programs whose output is the `sha256`, length, reverse, or uppercase of *their own
source* — plus a self-editing program (a counter that counts up while every other byte stays put).
Self-reference is purely *syntactic*: it adds no computing power and runs into Gödel / Tarski / Rice.
</details>

### 2. You can never fully predict yourself — [`self_model`](complife/self_model.py)

**In plain words:** If your picture of the world has to include a picture of *you*, then you can never predict yourself perfectly. There's always some leftover "self-surprise," and the smaller your memory, the bigger it gets. The twist: the rule *"to steer something well, you have to model it"* turns out to be the **exact same rule**. Steering and self-knowing are one and the same.

<details><summary>The precise version (for the curious)</summary>

An exact self-including model is impossible (`b` bits name at most `2^b` states; the world holding
the model has more). The residual obeys `H(T|M) ≥ H(T) − b`, shown here for an **arbitrary** model
(not a convenient one), with confidence intervals, across uniform/Zipf/Markov data. The
**Conant–Ashby good-regulator theorem** is *demonstrated*, not cited: brute-forcing every controller
shows the optimal one is forced to be a model of what it controls, with residual disorder exactly
`H(D) − b` — the same floor.
</details>

### 3. Copying yourself works — but only up to a limit — [`replication`](complife/replication.py)

**In plain words:** We build a tiny "organism": a machine plus a tape used two ways. The tape is *read* to build the machine, and *copied* untouched into the offspring. It reproduces byte-for-byte and passes mutations to its kids. That's von Neumann's 1948 blueprint for self-reproduction — sketched *before* anyone understood DNA. But there's a hard limit, found by Eigen: copy with **too many errors** and the message dissolves into noise. That's *why viruses can't have huge genomes* — and why some antiviral drugs work by nudging a virus's copy-error rate just past the cliff.

<details><summary>The precise version (for the curious)</summary>

Part A: a working von Neumann dual-use-tape replicator (`child == parent` byte-identical, the child
self-boots from its own bytes, mutations inherit). Part B: **Eigen's error threshold** — the fittest
sequence survives only while `μ·L < ln σ` — computed three ways (closed form; the full quasispecies
distribution as the leading eigenvector of the exact mutation–selection matrix, checked against
brute force to ~10⁻¹⁶; and a finite-population simulation), all agreeing.
</details>

### 4. Physics sets the ceilings — [`physical_limits`](complife/physical_limits.py)

**In plain words:** Physics caps every computer: how much it can store, how fast it can run, the least energy one bit can cost. The surprise: a brain uses a **tiny sliver** of these limits. Life isn't crammed to the physical brim — it's astonishingly roomy. This is also the one place the project touches a speculative physics idea, and it's careful to mark that part as a *boundary*, not a proven mechanism.

<details><summary>The precise version (for the curious)</summary>

Landauer (a bit costs ≥ `kT·ln2` = 2.87×10⁻²¹ J at 300 K), Bekenstein & holographic storage bounds,
and computed **speed ceilings** (Margolus–Levitin ≈ 7.6×10⁵⁰ ops/s for a brain, Bremermann, Lloyd).
The brain sits ~10⁻²⁷ of its storage ceiling and ~10⁻³⁶ below its speed ceiling, yet burns ~10⁶–10⁷×
the Landauer minimum per operation. The speculative NVG section is explicitly model-dependent —
[`NVG_INTERFACE.md`](NVG_INTERFACE.md).
</details>

## Two more walls, freshly added

The same "prove it, don't assert it" treatment, extending the picture:

### 5. Quantum states can't be copied at all — [`quantum`](complife/quantum.py)

**In plain words:** Part 3 showed *classical* copying is easy. Quantum information says the
opposite: you **cannot copy an unknown quantum state** — full stop. Try to, and physics hands you
an entangled mess instead of a copy. We show this in ~40 lines of linear algebra, two independent
ways, and contrast it with the classical bits that *can* be copied (which is exactly what lets
life reproduce). Copying: cheap for bits, forbidden for quantum states.

### 6. "Intelligence is compression," made precise — [`induction`](complife/induction.py)

**In plain words:** The best way to predict a sequence is to find the **shortest program** that
makes it (Solomonoff, Hutter). We show a tiny "shortest-program" search crack a stream that *looks*
totally random — recovering the hidden generator from a handful of samples and compressing it
**1000×**, where ordinary statistics is helpless. And we show the honest flip side: on **truly**
random data, nothing beats the entropy. Compression finds structure — but it can't invent it.

## Try it yourself

```bash
pip install -e .        # only needs Python 3.9+ and numpy
python -m complife      # runs all six parts and prints PASS/FAIL for each
```

Each part explains what it's doing and checks itself as it goes. Run just one with
`python -m complife 03`; the original numbered scripts still work too
(`python3 01_self_reference_quine.py`).

## Where this is actually useful

It's a foundations project, but several results connect to real things:

- **Learning & reference** — a runnable, honest tour of self-reference, prediction limits, heredity,
  and the physics of computation, with each claim tied to a test in [`CLAIMS.md`](CLAIMS.md).
- **A reality check** on grand claims about minds, compression, and "digital physics" — a template
  for separating what's proven from what's marketing.
- **Real-world hooks:**
  - Eigen's threshold is the theory behind *lethal-mutagenesis antivirals*.
  - The self-prediction floor bounds *introspective / self-monitoring AI*.
  - Landauer and the speed limits frame *the energy cost of computation* (timely for AI datacenters).
  - The good-regulator law is a *controller-sizing* rule.

## Honesty first

Taking it seriously means being clear about what it does **not** claim:

- **Every headline statement is backed by a test.** [`CLAIMS.md`](CLAIMS.md) maps each claim to the
  function and test that proves it. `make test` runs all 51 in ~8 seconds.
- **It does not explain consciousness.** "A self-modeling, self-editing program = self-awareness" is
  an unproven philosophical leap, and this project refuses to make it.
- **It invents no new physics and beats no known limit.** Just classic information theory + cybernetics
  (Kleene, Conant–Ashby, von Neumann, Eigen, Shannon, Solomonoff/Hutter). The one exotic-physics link
  (NVG) is a clearly-labeled *boundary*, never a mechanism — [`NVG_INTERFACE.md`](NVG_INTERFACE.md).

## Known limitations

Being a serious project also means naming the edges:

- **`replication` itself stays physics-free** (that's the point — modules 1–3 are substrate-independent).
  The *energy* of copying now lives where physics belongs: `physical_limits` computes the Landauer
  floor per genome copy and bridges it to Eigen's threshold — and finds DNA replication runs only
  ~10–100× above the thermodynamic minimum (near-optimal), vs ~10⁶–10⁸× for brains and LLMs.
- **`induction` uses a small, explicit hypothesis class.** True Solomonoff induction is
  uncomputable, so the shortest-program search is an honest approximation — exactly what real
  compressors do — not the ideal.
- **The NVG section is model-dependent by construction.** `ρ_c` and `M_crit` rest on asserted
  inputs (the 859 MeV scale, the melt mechanism); only their internal geometric consistency is
  tested — never treated as first-principles predictions. See [`NVG_INTERFACE.md`](NVG_INTERFACE.md).

## For developers

```bash
make test        # full suite (fast unit tests + slower Monte-Carlo / subprocess checks)
make test-fast   # skip the slow ones
make lint        # ruff
```

```
complife/            the tested package
  self_reference.py  quines, recursion theorem, Rice's theorem, self-editing programs
  self_model.py      self-prediction floor, good regulator, multi-agent, weight quantization
  replication.py     the self-copying organism, Eigen's threshold, fitness landscapes
  physical_limits.py storage / speed / energy ceilings, LLM vs Landauer
  quantum.py         the no-cloning wall
  induction.py       prediction = compression (Solomonoff / MDL)
tests/               one test file per part (72 tests total)
CLAIMS.md            every claim -> the function -> the test that proves it
```

Standard library + numpy. Fully deterministic (fixed seeds), MIT-licensed.
