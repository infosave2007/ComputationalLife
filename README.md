# Computational Life

[![CI](https://github.com/infosave2007/ComputationalLife/actions/workflows/ci.yml/badge.svg)](.github/workflows/ci.yml)
![python](https://img.shields.io/badge/python-3.9%2B-blue)
![license](https://img.shields.io/badge/license-MIT-green)

🇷🇺 Русская версия: [README.ru.md](README.ru.md)

**A runnable, self-checking answer to one question: what does it actually take — in provable
math, not hand-waving — for something to copy itself, know itself, and change itself?** These
are the core tricks we associate with life and mind. This project shows each one is an old,
exact theorem, and turns it into a tiny program you can run and verify in seconds.

## The problem it solves

Big claims about life, mind, "self-awareness," "compression is intelligence," "the universe is a
computer" are everywhere — and almost all of them are vague, untestable, or overhyped. You can't
tell a **proof** from a **poem**.

This repository fixes that for a specific, important cluster of those claims: it converts each one
into a small program that **either passes or fails when you run it**. Philosophy you can execute.
Concretely, it gives checkable answers to questions people usually only argue about:

- **Can a program really copy itself — or rewrite itself?** Yes. Here's a 75-character program
  that prints itself, and one that edits itself.
- **Can you ever fully predict yourself?** No — and there's an exact floor on how much of yourself
  must stay unpredictable. (Surprisingly, this is the *same* law as "to control something, you must
  model it.")
- **Why can't a self-copying thing carry unlimited information?** Because copying with too many
  errors destroys the message — a hard threshold. It's why viruses can't have huge genomes.
- **What are the physical limits of any computer, and how close is a brain to them?** Astonishingly
  far — a brain uses about a trillionth of a trillionth of its storage ceiling.

And, just as important, it draws a **hard line between what's proven and what's speculation** (the
one place it touches exotic physics is fenced off and labeled, not smuggled in as fact).

## Why it exists

Two reasons. First, to give **one honest, unified, tested foundation** for "life and mind as
computation" — instead of the usual scattered arm-waving, a single picture where self-reproduction,
self-modeling, self-reference, prediction, and physical limits are all the *same* idea, each proven.
Second, as a **reality check and teaching tool**: a place where grand claims about minds and
machines get grounded or rejected, with code anyone can rerun.

It is **not** a product or a practical utility. Its output is understanding you can trust.

## The one idea behind all of it

Look closely at anything alive or intelligent and you keep seeing the **same design**: a small set
of instructions plus a powerful machine that unfolds them.

- A **zip file** is a few kilobytes + an unzipper that rebuilds the whole thing.
- A **genome** is a recipe + the chemistry that grows it into an animal.
- Your **sense of self** is a compressed little model + a brain that runs it.

The recipe is cheap; the power lives in the decoder. This project makes that idea exact — and
shows where each version of it **hits a wall it can never cross**.

## The four parts

Each starts in plain words; the precise math is tucked into a "for the curious" box.

### 1. A thing can refer to itself — [`self_reference`](complife/self_reference.py)

**In plain words:** A program can print its own source code exactly — a "quine," like a sentence
that perfectly describes itself (smallest here: **75 characters**). It can go further: compute
*anything about itself* and even **rewrite itself** — the math behind self-copying code and
reflection. The catch: a system can point at itself forever but can **never fully "understand"
itself** (Gödel's limit).

<details><summary>The precise version (for the curious)</summary>

**Kleene's recursion theorem.** Self-reference exists in every general-purpose language, and adding
"also reproduce yourself" to any program costs only a fixed number of bytes (shown exactly: a
constant 76-byte overhead for arbitrary content). We also build the **second recursion theorem**
constructively — programs whose output is the `sha256`, length, reverse, or uppercase of *their own
source* — plus a self-editing program (a counter that counts up while every other byte stays put).
Self-reference is purely *syntactic*: it adds no computing power and runs into Gödel / Tarski / Rice.
</details>

### 2. You can never fully predict yourself — [`self_model`](complife/self_model.py)

**In plain words:** If your model of the world must include a model of *you*, you can never predict
yourself perfectly — there's an unavoidable floor of "self-surprise," and the smaller your memory
budget, the bigger it is. The twist: the rule *"to control something well, you must model it"* turns
out to be the **exact same inequality**. Steering and self-knowing are one law.

<details><summary>The precise version (for the curious)</summary>

An exact self-including model is impossible (`b` bits name at most `2^b` states; the world holding
the model has more). The residual obeys `H(T|M) ≥ H(T) − b`, shown here for an **arbitrary** model
(not a convenient one), with confidence intervals, across uniform/Zipf/Markov data. The
**Conant–Ashby good-regulator theorem** is *demonstrated*, not cited: brute-forcing every controller
shows the optimal one is forced to be a model of what it controls, with residual disorder exactly
`H(D) − b` — the same floor.
</details>

### 3. Copying yourself works — but only up to a limit — [`replication`](complife/replication.py)

**In plain words:** We build a tiny "organism" — a machine plus a tape used two ways: *read* to
build the machine, and *copied* untouched to the offspring. It reproduces byte-for-byte and passes
on mutations. That's von Neumann's 1948 blueprint for self-reproduction — before DNA was understood.
But there's a hard limit (Eigen's): copy with **too many errors** and the message dissolves into
noise. It's *why viruses can't have huge genomes* — and why some antiviral drugs work by pushing a
virus's copy-error rate just past the cliff.

<details><summary>The precise version (for the curious)</summary>

Part A: a working von Neumann dual-use-tape replicator (`child == parent` byte-identical, the child
self-boots from its own bytes, mutations inherit). Part B: **Eigen's error threshold** — the fittest
sequence survives only while `μ·L < ln σ` — computed three ways (closed form; the full quasispecies
distribution as the leading eigenvector of the exact mutation–selection matrix, checked against
brute force to ~10⁻¹⁶; and a finite-population simulation), all agreeing.
</details>

### 4. Physics sets the ceilings — [`physical_limits`](complife/physical_limits.py)

**In plain words:** Physics caps any computer — how much it can store, how fast it can run, the least
energy a bit can cost. The surprise: a brain uses a **staggeringly tiny slice** of these ceilings.
Life isn't packed to the physical brim — it's astonishingly sparse. This is also the one place the
project touches a speculative physics idea, and it's careful to mark that part as a *boundary*, not a
mechanism.

<details><summary>The precise version (for the curious)</summary>

Landauer (a bit costs ≥ `kT·ln2` = 2.87×10⁻²¹ J at 300 K), Bekenstein & holographic storage bounds,
and computed **speed ceilings** (Margolus–Levitin ≈ 7.6×10⁵⁰ ops/s for a brain, Bremermann, Lloyd).
The brain sits ~10⁻²⁷ of its storage ceiling and ~10⁻³⁶ below its speed ceiling, yet burns ~10⁶–10⁷×
the Landauer minimum per operation. The speculative NVG section is explicitly model-dependent —
[`NVG_INTERFACE.md`](NVG_INTERFACE.md).
</details>

## Where this is actually useful

It's a foundations project, but several results connect to real things:

- **Learning & reference** — a runnable, honest tour of self-reference, prediction limits, heredity,
  and the physics of computation, with each claim tied to a test in [`CLAIMS.md`](CLAIMS.md).
- **A reality check** on grand claims about minds, compression, and "digital physics" — a template
  for separating what's proven from what's marketing.
- **Real-world hooks:** Eigen's threshold is the theory behind *lethal-mutagenesis antivirals*; the
  self-prediction floor bounds *introspective / self-monitoring AI*; Landauer and the speed limits
  frame *the energy cost of computation* (timely for AI datacenters); the good-regulator law is a
  *controller-sizing* rule.

## Try it yourself

```bash
pip install -e .        # only needs Python 3.9+ and numpy
python -m complife      # runs all four parts and prints PASS/FAIL for each
```

Each part narrates what it's doing and checks itself as it goes. Run just one with
`python -m complife 03`; the original numbered scripts still work too
(`python3 01_self_reference_quine.py`).

## Honesty first

Taking it seriously means being clear about what it does **not** claim:

- Every headline statement is backed by a test — [`CLAIMS.md`](CLAIMS.md) maps each claim to the
  function and test that proves it. `make test` runs all 51 in ~8 seconds.
- **It does not explain consciousness.** "A self-modeling, self-editing program = self-awareness" is
  an unproven philosophical leap, and this project refuses to make it.
- **It invents no new physics and beats no known limit.** Classic information theory + cybernetics
  (Kleene, Conant–Ashby, von Neumann, Eigen, Shannon, Solomonoff/Hutter). The one exotic-physics link
  (NVG) is a clearly-labeled *boundary*, never a mechanism — [`NVG_INTERFACE.md`](NVG_INTERFACE.md).

## For developers

```bash
make test        # full suite (fast unit tests + slower Monte-Carlo / subprocess checks)
make test-fast   # skip the slow ones
make lint        # ruff
```

```
complife/            the tested package
  self_reference.py  quines, the recursion theorem, self-editing programs
  self_model.py      the self-prediction floor, the good-regulator theorem
  replication.py     the self-copying organism, Eigen's error threshold
  physical_limits.py storage / speed / energy ceilings
tests/               one test file per part (51 tests total)
CLAIMS.md            every claim -> the function -> the test that proves it
```

Standard library + numpy. Fully deterministic (fixed seeds), MIT-licensed.
