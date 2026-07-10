# Claims → function → test → caveat

Every headline claim in this repository, the function that computes it, the test that
verifies it independently, and the honest caveat. If a row's test fails, the claim is
false — that is the point. Run `make test` to check them all.

## `self_reference` — Kleene recursion theorem

| Claim | Function | Test | Caveat |
|---|---|---|---|
| A Python program's stdout equals its own 75 source bytes | `verify_python_quine` | `test_python_quine_reproduces` | verified in a fresh subprocess against the on-disk bytes |
| Underload `(:aSS):aSS` (10 sym) and a 99-byte Lisp λ-term reproduce themselves | `verify_underload`, `verify_lisp` | `test_underload_quine`, `test_lisp_quine` | interpreters implemented here; instances, not universal existence (that is Kleene's theorem) |
| A **constructed Brainfuck quine** reproduces itself in our interpreter | `brainfuck_quine`, `verify_brainfuck_quine` | `test_brainfuck_quine_reproduces_itself` | non-minimal (7377 B); generated & verified for this interpreter's conventions, not a remembered byte-string |
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
| On an arbitrary fitness landscape, a **flatter** peak out-grows a taller one past a crossover mutation rate | `quasispecies_landscape`, `survival_of_the_flattest` | `test_survival_of_the_flattest_crossover`, `test_landscape_reduces_to_single_peak` | "survival of the flattest" (Wilke 2001); winner = larger dominant eigenvalue |

## `physical_limits` — ceilings & the NVG boundary

| Claim | Function | Test | Caveat |
|---|---|---|---|
| Landauer: erase 1 bit ≥ 2.87×10⁻²¹ J at 300 K | `landauer_energy` | `test_landauer_room_temperature` | reversible computing can beat this |
| Bekenstein & holographic ceilings; brain uses ≪ 1 of them | `bekenstein_bits`, `holographic_bits`, `sparseness_table` | `test_bekenstein_...`, `test_sparseness_all_below_ceiling` | I_used figures are order-of-magnitude; conclusion robust to that |
| Speed ceilings: ML 7.6×10⁵⁰, Bremermann 1.36×10⁵⁰/kg, Lloyd 5.4×10⁵⁰ ops/s | `margolus_levitin_rate`, `bremermann_rate_per_kg`, `lloyd_ultimate_laptop` | `test_speed_ceilings` | upper bounds only; ML vs Bremermann differ by an O(1) convention |
| Landauer throughput at 20 W / 310 K ≈ 6.7×10²¹ erasures/s | `landauer_max_erasures_per_s` | `test_landauer_throughput_and_floor_inverse` | brain runs ~7 orders above the per-bit minimum |
| NVG core: `r_h = √3·l`, `S_BH = 3·S(l)`, density loop closes, `M_crit ≈ 0.99 M⊙` | `nvg_core` | `test_nvg_core_geometry_consistent` | `M_Ω = 859 MeV` and the melt mechanism are **NVG model inputs**, not derived; below `M_crit` there is no horizon, so core entropy is model-dependent |
| LLM inference runs ~10⁸× above the Landauer floor (~7.5 nJ/token) | `llm_landauer_floor_per_token`, `gpu_max_bit_erasures_per_s` | `test_llm_inference_far_above_landauer_floor` | I_used/energy figures are order-of-magnitude; conclusion (many orders above the floor) is robust |
| DNA replication is ~10–100× above the Landauer floor (near-optimal); Eigen fidelity caps genome size at ~10⁹ bp | `landauer_copy_energy`, `eigen_max_genome_bits` | `test_dna_replication_near_landauer_floor`, `test_eigen_max_genome_is_genome_scale` | the energy bridge from module 03; per-bp cost figures are order-of-magnitude |

## `self_model` — regulation, multi-agent & model compression (additions)

| Claim | Function | Test | Caveat |
|---|---|---|---|
| Several regulators' capacities **add**: residual `H(Z) = max(0, k − Σbᵢ)` | `multi_agent_residual` | `test_multi_agent_capacities_add` | holds when the agents observe disjoint slices of the disturbance |
| **Compressing a model's own weights raises its prediction cost** (excess grows as bits shrink) | `demo_quantization` | `test_weight_quantization_raises_prediction_cost` | the `H(T\|M) ≥ H(T) − b_M` floor applied to parameters — the honest core of the "quantization loses self-predictability" intuition |

## `quantum` — the fifth wall: no-cloning

| Claim | Function | Test | Caveat |
|---|---|---|---|
| Classical basis states copy perfectly (CNOT) | `clone_fidelity`, `classical_copy_works` | `test_classical_basis_states_clone` | this is what lets a classical replicator (module 03) exist |
| An unknown **superposition cannot be cloned**: CNOT entangles it (fidelity 1/2) | `clone_attempt_cnot`, `linearity_forces_entanglement` | `test_superposition_cannot_be_cloned_fidelity_half`, `test_clone_attempt_is_the_bell_state` | forced by *linearity*, not technology |
| No cloning unitary exists for non-orthogonal states (`⟨ψ\|φ⟩ = ⟨ψ\|φ⟩²`) | `inner_product_obstruction` | `test_inner_product_obstruction`, `test_random_nonorthogonal_pairs_forbid_cloning` | independent proof (unitarity preserves inner products) |

## `induction` — prediction = compression (Solomonoff / MDL)

| Claim | Function | Test | Caveat |
|---|---|---|---|
| A short-program search **recovers the generator** and crushes statistics on algorithmically-simple data | `infer_lcg`, `mdl_codelen` | `test_lcg_is_recovered_and_reproduces`, `test_mdl_beats_statistics_on_algorithmic_data` | hypothesis class is small & explicit; true Solomonoff is **uncomputable** |
| On **truly random** data no predictor beats the entropy (MDL correctly gives up) | `mdl_codelen`, `best_statistical_codelen` | `test_true_randomness_is_incompressible` | you cannot compress below Shannon / Kolmogorov |
| Two-part code (`\|program\| + \|data\|program\|`) compresses an LCG stream >100× | `mdl_codelen` | `test_two_part_code_compresses_lcg` | this is exactly the quantity the Hutter Prize scores |

## `self_reference` — Rice's theorem (addition)

| Claim | Function | Test | Caveat |
|---|---|---|---|
| **No decider of a non-trivial semantic property survives its own diagonal** program | `build_diagonal`, `verify_rice` | `test_rice_theorem_every_decider_refuted` | constructive halting/Rice: every candidate decider is refuted by a program built against it |
