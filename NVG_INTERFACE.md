# The NVG interface — an honest boundary, not a merger

This note answers the question *"where does the computational-life theory connect to
NVG physics?"* directly and without wishful thinking. The short answer: **at exactly one
place — physical resource ceilings — and there it is a boundary condition, not a
mechanism.** Everything beyond that is category error, and this document says why, so the
line is drawn once and does not have to be re-litigated.

The computational-life results (`01`–`03`) are **substrate-independent theorems**. They
hold on transistors, on DNA, on a Turing machine of pebbles — and on any spacetime NVG
describes. A substrate-independent theorem cannot be *derived from* a particular physics,
and a particular physics cannot add predictive content to it. So the only way physics can
touch it is by **bounding the hardware**.

## 1. The one legitimate bridge — resource ceilings (computed in `complife/physical_limits.py`)

Physics caps *any* computer. The first four are first-principles; the last is NVG-specific and
rests on **asserted model inputs** (the scale `M_Ω = 859 MeV` and the "vacuum melts" mechanism),
so it is flagged as such — the code checks only its geometric self-consistency.

| Ceiling | Statement | Value |
|---|---|---|
| Landauer | energy to erase one bit ≥ `kB·T·ln2` | 2.87×10⁻²¹ J @ 300 K |
| Bekenstein | bits in radius R, energy E ≤ `2πRE/(ℏc ln2)` | ~10⁴² for a brain |
| Holographic | bits ≤ area/(4 lP² ln2) (scales with **area**) | ~10⁶⁸ for a brain-sized region |
| Speed (Margolus–Levitin) | ops/s ≤ `4E/h` | ~7.6×10⁵⁰ for a brain |
| **NVG-specific** *(model input)* | energy density where the vacuum melts: `ρ_c = M_Ω⁴/(ℏc)³` | **1.26×10²⁰ kg/m³** |

The NVG number does something clean, once stated precisely. From `ρ_c` the extremal regular core
has an **inner de Sitter scale** `l = 1.128 km`, mass `M_crit ≈ 0.99 M⊙` (the extremal Hayward
mass), and — the geometry done correctly — a **merged horizon at `r_h = √3·l = 1.954 km`**. Two
distinct entropies live here, and they must not be conflated:

- the **area bound at the inner scale**, `S(l) = A(l)/(4 lP² ln2) ≈ 2.2×10⁷⁶ bits`;
- the **Bekenstein–Hawking entropy at the actual horizon**, `S_BH = A(r_h)/(4 lP² ln2) ≈ 6.6×10⁷⁶
  bits` (`= 3·S(l)`, since it scales with `r²`).

The earlier "the core *saturates* holography" was a near-tautology (a bound evaluated at its own
defining radius) computed at the wrong radius; the honest statement is the pair above. And note:
*below* `M_crit` the regular remnant has **no horizon**, so its thermodynamic entropy is
model-dependent and not asserted here. What survives is that NVG marks a *maximal information
density* `ρ_c` and a *collapse boundary* `M_crit ≈ 1 M⊙` for any hardware — a boundary condition,
contingent on the NVG postulates.

**But note what this is and isn't.** It bounds **storage capacity — the container**. It is
the same quantity we separated from data compressibility earlier this session (physical
bits/m³ ≠ message entropy) and from computation. NVG's `ρ_c` tells you the smallest box that
holds N bits; it says nothing about whether those N bits could be fewer (compression), nor
about whether the box *computes* (it doesn't).

**A secondary, weaker bridge is shared mathematics, not shared mechanism:** the no-hair
picture — a black hole's exterior is fixed by `(M, J, Q)` plus GR "decoding" the metric for
free — is literally the *"few-parameter program + free decoder"* pattern, i.e. `K(exterior |
GR)` is tiny. This is a genuine instance of generative compression. But it is **generic
general relativity, not NVG**, and it is **lossy** (that lossiness *is* the information
paradox). It illustrates the pattern; it grounds nothing NVG-specific.

## 2. What does NOT connect — category errors (stated once, closed)

### 2a. "A black-hole core is a self-developing copy, like a zygote" — **category error**

A regular core is a *static* solution of gravity + the W-field (exact Schwarzschild outside
by Birkhoff; de-Sitter core inside). Run it against von Neumann's criteria for a
self-replicator and it fails **every one**:

| von Neumann requirement | zygote | black-hole core |
|---|---|---|
| separable, copyable description/tape | genome | **no** (`M` is one number, not a program) |
| constructor that *interprets* the description | ribosome | **no** (physics minimizes an action; it does not read a tape) |
| copier (verbatim replication) | polymerase | **no** (there is no copy event) |
| offspring = copy of self + description | daughter cell | **no** (mergers are N→1; evaporation is thermal destruction) |
| computation over information | yes | **no** (fixed metric, no memory, no logic) |
| self-development (phenotype unfolding) | ontogeny | **no** (static; passive W-resonance ≠ morphogenesis) |
| heritable variation + selection | yes | **no** (no genome to mutate/copy/select) |

*(Two independent adversarial verifiers this session returned **category-error** on this
claim.)* The zygote passes all seven; the core passes none. Storage density is not
reproduction.

### 2b. "Consciousness raises information density → critical → the bounce" — **no mechanism**

There is no operational definition of "information density of consciousness" (in what units?),
no term coupling it to the W-field action `S[g, 𝒲]`, and no falsifiable consequence. The
bounce in NVG is triggered by *mass-energy* reaching `ρ_c`, a QCD quantity — nothing about an
observer. Grafting consciousness on has no free parameter it explains and no number it
predicts; the model is complete without it.

### 2c. "NVG-Zip beats Shannon" — **false**

The `NVG_DATA_COMPRESSION` prototype is lossy/generative with no round-trip codec; its
"1044×" is the ratio of deleting ~99.9% of the bytes and refilling with matched-variance
noise. No lossless codec can go below the source entropy (Shannon), and no physical/quantum
principle changes that (three independent verifiers confirmed). "Compression = intelligence"
is real (`02`,`04`); "compression via gravity" is not.

## 3. The honest meta-conclusion

- Computational life is **substrate-independent** (von Neumann + Turing + Solomonoff/Hutter).
  NVG is **a substrate**. They meet only where physics caps the hardware.
- NVG **neither derives nor is derived from** the computational-life theory, and adds **no
  predictive content** to it. The genuine, computed interface is a *ceiling*: `ρ_c` and
  `M_crit ≈ 1 M⊙` mark the maximal physical information **density** and the collapse boundary.
- Everything richer — cores as organisms, consciousness as a density field, gravity as a
  compressor — is metaphor at best and numerology at worst, of exactly the kind already
  purged from the NVG repository this session.

The interface is real, it is small, and it is a **boundary**. Drawing it precisely is what
lets the beautiful part — one computational theory of life and mind — stand on its own,
unweakened by a physics it does not need.
