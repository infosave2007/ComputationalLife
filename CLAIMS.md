# Claims → function → test → caveat

Every headline claim in this repository, the function that computes it, the test that
verifies it independently, and the honest caveat. If a row's test fails, the claim is
false — that is the point. Run `make test` to check them all.

## `self_reference` — Kleene recursion theorem

| Claim | Function | Test | Caveat |
|---|---|---|---|
| A Python program's stdout equals its own 75 source bytes | `verify_python_quine` | `test_python_quine_reproduces` | verified in a fresh subprocess against the on-disk bytes |
| Underload `(:aSS):aSS` (10 sym) and a 99-byte Lisp λ-term reproduce themselves | `verify_underload`, `verify_lisp` | `test_underload_quine`, `test_lisp_quine` | interpreters implemented here; instances, not universal existence (that is Kleene's theorem) |
| A program can output a **nontrivial function of its own source** | `build_self_applying`, `verify_second_recursion_theorem` | `test_second_recursion_theorem_all_g`, `..._sha256_value` | tested for `g ∈ {sha256, length, reverse, upper}`; `g` must be total & side-effect-free |
| A program can **rewrite itself** (counter n→n+1, rest invariant) | `self_modifier`, `verify_self_modification` | `test_self_modification_counter_and_invariance` | fixed-width counter field; Python forbids zero-padded int literals so the counter is a string |
| Making a program self-reproducing costs an **additive constant** | `augment_via_self_read`, `measure_self_read_overhead` | `test_self_read_overhead_constant_across_payloads`, `test_self_read_programs_reproduce_source` | exactly constant (76 B) for arbitrary bytes; the self-reading tail is not a strict no-input quine |
| The repr construction's overhead is `159 + #escapes` | `characterise_repr_overhead` | `test_repr_overhead_is_159_plus_escapes` | `O(#escapes)`, **not** constant for arbitrary bytes — the honest limitation |

## `self_model` — good regulator & the lossy self-model

| Claim | Function | Test | Caveat |
|---|---|---|---|
| Exact self-inclusive modeling is impossible (`2^{b_M} < |T|`) | `analyse` | `test_analytic_impossibility_and_ratio` | requires the target to contain the model plus ≥1 more bit |
| `H(T\|M) ≥ H(T) − b_M` for an **arbitrary** deterministic `g` | `random_hash_model`, `dpi_check` | `test_dpi_floor_holds_for_arbitrary_random_g` | needs `n/2^{b_M} ≳ 30` for a good `H(M)` estimate |
| The bound is a genuine lower bound (wasteful `g` sits above it) | `random_hash_model(distinct_bits<b_M)` | `test_wasteful_g_sits_strictly_above_floor` | — |
| The floor holds on non-uniform / Markov sources; prefix isn't optimal | `zipf_source`, `markov_source`, `greedy_partition_model` | `test_greedy_beats_prefix_on_skewed_source` | greedy partition is a strong heuristic, not provably global optimum |
| The **optimal regulator is forced to be a model** of the disturbance | `optimal_regulator` | `test_conant_ashby_optimal_regulator_is_a_model` | finite illustrative instance (`Z=(D+R) mod n`), not a new proof; unique up to goal relabeling |
| A `b`-bit regulator has residual `H(Z) = H(D) − b` | (demo) | `test_conant_ashby_bit_budget_matches_self_model_floor` | same data-processing floor as the self-model bound |
| MM / Grassberger estimators are within milli-bits of the truth | `entropy_*`, `bootstrap_entropy_ci` | `test_entropy_*`, `test_bootstrap_ci_brackets_truth` | plug-in is biased low; the bound itself is analytic |

## `replication` — von Neumann tape & Eigen quasispecies

| Claim | Function | Test | Caveat |
|---|---|---|---|
| `child == parent`, `grandchild == child` (self-boot) | `replicate_via_own_machinery` | `test_replicator_child_and_grandchild_identical` | — |
| A tape mutation is inherited verbatim | `mutate_payload` | `test_mutation_inherited_verbatim` | — |
| Parent→child is a payload-length-independent operator | `build_organism` | `test_machinery_independent_of_payload_length` | `K(child) ≤ K(parent)+O(1)` is the *operator*, not the (trivial) identity |
| Error threshold `μ_crit·L → ln σ`, **from below**, for a range of σ | `critical_mu`, `critical_mu_numeric` | `test_threshold_approaches_ln_sigma_from_below_monotone`, `test_threshold_general_sigma` | **fixes an earlier bug** where a fixed-iteration solver overshot to `>1` |
| The **full** quasispecies eigenvector matches brute-force `2^L` | `quasispecies_distribution`, `quasispecies_bruteforce` | `test_lumped_quasispecies_matches_bruteforce` | exact Hamming-class lumping; agreement `~10⁻¹⁶` |
| The full model's master fraction is smooth & >0 at finite L | `quasispecies_distribution` | `test_full_model_master_fraction_smooth_positive` | the sharp catastrophe is the `L→∞` / no-back-mutation limit |
| Finite-N Wright–Fisher persists below / collapses above threshold | `wf_survival_curve` | `test_wright_fisher_persists_and_collapses` | exact `numpy` binomial (fixes a Gaussian-approx + rare `log(0)` crash) |

## `physical_limits` — ceilings & the NVG boundary

| Claim | Function | Test | Caveat |
|---|---|---|---|
| Landauer: erase 1 bit ≥ 2.87×10⁻²¹ J at 300 K | `landauer_energy` | `test_landauer_room_temperature` | reversible computing can beat this |
| Bekenstein & holographic ceilings; brain uses ≪ 1 of them | `bekenstein_bits`, `holographic_bits`, `sparseness_table` | `test_bekenstein_...`, `test_sparseness_all_below_ceiling` | I_used figures are order-of-magnitude; conclusion robust to that |
| Speed ceilings: ML 7.6×10⁵⁰, Bremermann 1.36×10⁵⁰/kg, Lloyd 5.4×10⁵⁰ ops/s | `margolus_levitin_rate`, `bremermann_rate_per_kg`, `lloyd_ultimate_laptop` | `test_speed_ceilings` | upper bounds only; ML vs Bremermann differ by an O(1) convention |
| Landauer throughput at 20 W / 310 K ≈ 6.7×10²¹ erasures/s | `landauer_max_erasures_per_s` | `test_landauer_throughput_and_floor_inverse` | brain runs ~7 orders above the per-bit minimum |
| NVG core: `r_h = √3·l`, `S_BH = 3·S(l)`, density loop closes, `M_crit ≈ 0.99 M⊙` | `nvg_core` | `test_nvg_core_geometry_consistent` | `M_Ω = 859 MeV` and the melt mechanism are **NVG model inputs**, not derived; below `M_crit` there is no horizon, so core entropy is model-dependent |
