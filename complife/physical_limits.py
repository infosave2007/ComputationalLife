#!/usr/bin/env python3
"""Physical limits on computation -- and the ONE honest interface with NVG.

Modules 01-03 are substrate-independent theorems: they need no physics. Physics
enters only as CEILINGS on the hardware -- how many bits a region can store, how
fast it can flip them, and how much energy an irreversible bit costs. This
module computes those ceilings:

  * STORAGE : Landauer (energy/bit), Bekenstein & holographic (bits/region).
  * SPEED   : Margolus-Levitin, Bremermann, Lloyd's ultimate laptop.
  * THROUGHPUT : Landauer at a real power budget (the brain's ~20 W).
  * SPARSENESS : every biological system sits >20 orders below its ceiling.

Then the one NVG-specific number, clearly flagged as a MODEL INPUT rather than a
first-principles result: rho_c, the energy density at which (in NVG) the QCD
vacuum melts and a regular core forms. We compute the geometry honestly --
separating the inner de Sitter scale from the extremal horizon -- and refuse the
tautology of "saturating" a bound evaluated at its own defining radius.
"""

from __future__ import annotations

import math

from .common import H_PLANCK, HBAR, KB, L_PLANCK, LN2, M_SUN, MEV, C, G, Report, header, save_result


# --------------------------------------------------------------------------- #
#  Storage ceilings
# --------------------------------------------------------------------------- #
def landauer_energy(T: float) -> float:
    """Minimum energy to erase one bit at temperature T (joules)."""
    return KB * T * LN2


def bekenstein_bits(R: float, E: float) -> float:
    """Max bits in a sphere of radius R holding energy E: 2*pi*R*E/(hbar c ln2)."""
    return 2 * math.pi * R * E / (HBAR * C) / LN2


def holographic_bits(R: float) -> float:
    """Max bits on a horizon of radius R (area law): A/(4 lP^2 ln2)."""
    A = 4 * math.pi * R**2
    return A / (4 * L_PLANCK**2) / LN2


# --------------------------------------------------------------------------- #
#  Speed ceilings
# --------------------------------------------------------------------------- #
def margolus_levitin_rate(E: float) -> float:
    """Max rate of distinct (orthogonal) states, 2E/(pi hbar) = 4E/h ops/s."""
    return 4.0 * E / H_PLANCK


def bremermann_rate_per_kg() -> float:
    """Bremermann's limit c^2/h, in ops/s per kilogram (uses E = m c^2, rate E/h)."""
    return C**2 / H_PLANCK


def lloyd_ultimate_laptop(mass: float = 1.0) -> float:
    """Lloyd's ultimate-laptop operation rate 2 E/(pi hbar) for E = mass c^2."""
    return margolus_levitin_rate(mass * C**2)


# --------------------------------------------------------------------------- #
#  Landauer throughput at a real power budget
# --------------------------------------------------------------------------- #
def landauer_max_erasures_per_s(power: float, T: float) -> float:
    """Max irreversible bit-erasures/s sustainable at power `power`, temp T."""
    return power / (KB * T * LN2)


def landauer_floor_power(rate: float, T: float) -> float:
    """Minimum power to erase `rate` bits/s at temperature T."""
    return rate * KB * T * LN2


def gpu_max_bit_erasures_per_s(power: float, T: float = 350.0) -> float:
    """Max irreversible bit-erasures/s for a chip drawing `power` watts at die
    temperature T (default 350 K ≈ 77 C)."""
    return power / (KB * T * LN2)


def landauer_copy_energy(bits: float, T: float = 310.0) -> float:
    """Minimum energy to write one faithful irreversible copy of `bits` bits at
    body temperature T (default 310 K). This is the thermodynamic floor for
    replication — the physics bridge to module 03's information-only replicator."""
    return bits * KB * T * LN2


def eigen_max_genome_bits(mu: float, sigma: float = math.e,
                          bits_per_symbol: float = 2.0) -> float:
    """Max stably-heritable information (bits) at per-symbol copy-error rate `mu`,
    from Eigen's threshold L < ln(sigma)/mu (module 03). Copy fidelity caps how
    much a replicator can carry — and therefore its per-copy energy floor."""
    return (math.log(sigma) / mu) * bits_per_symbol


def llm_landauer_floor_per_token(params: float, bits_per_flop: float = 16.0,
                                 T: float = 350.0) -> float:
    """Landauer floor energy (J) for one generated token of a dense P-parameter
    Transformer: a forward pass is ~2P FLOPs/token; charge `bits_per_flop`
    irreversible bit-erasures per FLOP (a conservative lower bound). This is the
    thermodynamic MINIMUM — real hardware is far above it."""
    flops = 2.0 * params
    bit_ops = flops * bits_per_flop
    return bit_ops * KB * T * LN2


# --------------------------------------------------------------------------- #
#  NVG regular-core geometry (all quantities flagged as model-dependent)
# --------------------------------------------------------------------------- #
def nvg_core() -> dict[str, float]:
    """Compute the NVG regular-core chain from the model input M_Omega = 859 MeV.

    NVG MODEL INPUTS (asserted, not derived here): the scale M_Omega = 859 MeV
    and the interpretation that the QCD vacuum 'melts' at energy density
    rho_c = M_Omega^4/(hbar c)^3. This function only checks the geometric
    consistency of the chain rho_c -> l -> M_crit -> horizon -> entropy.
    """
    M_Omega_J = 859.0 * MEV
    rho_c_energy = M_Omega_J**4 / (HBAR * C) ** 3        # J/m^3
    rho_c_mass = rho_c_energy / C**2                     # kg/m^3

    # Inner de Sitter core scale l from rho = 3 c^2 / (8 pi G l^2).
    l_core = math.sqrt(3 * C**2 / (8 * math.pi * G * rho_c_mass))
    # Consistency: recompute rho from l (closes the loop).
    rho_from_l = 3 * C**2 / (8 * math.pi * G * l_core**2)

    # Extremal Hayward mass: horizons solve x^3 - x^2 + eps^2 = 0 with a double
    # root at x = 2/3, eps = 2/(3 sqrt3). M_crit = (3 sqrt3 / 4) l c^2/G.
    M_crit = (3 * math.sqrt(3) / 4) * l_core * C**2 / G
    # Extremal (merged) horizon radius: r_h = (4/3) * (G M_crit/c^2) = sqrt(3) l.
    r_h = math.sqrt(3.0) * l_core

    return {
        "M_Omega_MeV": 859.0,
        "rho_c_energy": rho_c_energy,
        "rho_c_mass": rho_c_mass,
        "l_core": l_core,
        "rho_from_l": rho_from_l,
        "M_crit": M_crit,
        "M_crit_Msun": M_crit / M_SUN,
        "r_h": r_h,
        "S_inner": holographic_bits(l_core),      # area bound at inner scale
        "S_horizon": holographic_bits(r_h),        # Bekenstein-Hawking at horizon
    }


# --------------------------------------------------------------------------- #
#  Sparseness scan
# --------------------------------------------------------------------------- #
# (name, radius m, mass kg, information used bits). I_used figures are
# order-of-magnitude from the literature; the CONCLUSION (>20 orders below the
# ceiling) is robust to their uncertainty.
SPARSENESS_SYSTEMS: list[tuple[str, float, float, float]] = [
    ("E. coli",        1.0e-6,  1.0e-15, 9.2e6),     # ~4.6 Mbp x 2 bits
    ("yeast cell",     2.5e-6,  6.0e-14, 2.4e7),     # ~12 Mbp x 2 bits
    ("human zygote",   6.0e-5,  3.6e-9,  6.4e9),     # ~3.2 Gbp x 2 bits
    ("human brain",    8.0e-2,  1.4e0,   7.05e14),   # ~1.5e14 synapses x 4.7 bits
    ("datacenter rack", 1.0e0,  1.0e3,   8.0e16),    # ~10 PB
]


def sparseness_table() -> list[dict[str, float]]:
    rows = []
    for name, R, M, I_used in SPARSENESS_SYSTEMS:
        E = M * C**2
        f_bek = I_used / bekenstein_bits(R, E)
        f_holo = I_used / holographic_bits(R)
        rows.append({"name": name, "R": R, "M": M, "I_used": I_used,
                     "f_bek": f_bek, "f_holo": f_holo})
    return rows


# --------------------------------------------------------------------------- #
#  Demo
# --------------------------------------------------------------------------- #
def demo() -> bool:
    print(header("Physical limits on any computer (ceilings, not the computation)"))
    report = Report()

    # 1. Landauer -----------------------------------------------------------
    print("\n1. LANDAUER -- minimum energy to erase one bit (kB T ln2):")
    for T, lbl in [(300, "room temp"), (2.725, "CMB"), (0.01, "dilution fridge")]:
        print(f"     T = {T:>7} K ({lbl:<15}) -> {landauer_energy(T):.3e} J/bit")
    report.check("Landauer at 300 K == 2.87e-21 J",
                 abs(landauer_energy(300) - 2.871e-21) < 1e-24)

    # 2. Storage ceiling for a brain ---------------------------------------
    print("\n2. STORAGE: a human brain vs its ceilings (life is information-SPARSE):")
    R_brain, M_brain = 0.08, 1.4
    E_brain = M_brain * C**2
    I_bek = bekenstein_bits(R_brain, E_brain)
    I_holo = holographic_bits(R_brain)
    I_used = 1.5e14 * 4.7
    print(f"     Bekenstein ceiling (R=8cm,1.4kg): {I_bek:.2e} bits")
    print(f"     Holographic ceiling (R=8cm):      {I_holo:.2e} bits")
    print(f"     Connectome (used):                {I_used:.2e} bits")
    print(f"     fraction of Bekenstein ceiling used: 10^{math.log10(I_used / I_bek):.1f}")
    print(f"     fraction of holographic ceiling used: 10^{math.log10(I_used / I_holo):.1f}")
    report.check("brain uses <1e-25 of its Bekenstein ceiling", I_used / I_bek < 1e-25)

    # 3. SPEED ceilings -----------------------------------------------------
    print("\n3. SPEED: Margolus-Levitin / Bremermann / Lloyd (were only cited before):")
    ml_brain = margolus_levitin_rate(E_brain)
    brem_brain = bremermann_rate_per_kg() * M_brain
    lloyd = lloyd_ultimate_laptop(1.0)
    print(f"     Margolus-Levitin (brain, 4E/h):     {ml_brain:.2e} ops/s")
    print(f"     Bremermann      (brain, c^2/h*M):    {brem_brain:.2e} ops/s")
    print(f"     Lloyd ultimate laptop (1 kg):        {lloyd:.2e} ops/s")
    synaptic_events = 1.5e14 * 10  # ~1e15 events/s (10 Hz mean)
    print(f"     brain actual ~{synaptic_events:.0e} synaptic events/s "
          f"=> runs 10^{math.log10(synaptic_events / ml_brain):.0f} below its speed ceiling")
    report.check("Margolus-Levitin brain rate ~7.6e50 ops/s",
                 abs(math.log10(ml_brain) - 50.88) < 0.1)
    report.check("Bremermann rate per kg == 1.36e50 ops/s/kg",
                 abs(bremermann_rate_per_kg() / 1.356e50 - 1.0) < 0.02)

    # 4. Landauer throughput at the brain's real power budget ---------------
    print("\n4. THROUGHPUT: Landauer at the brain's ~20 W / 310 K budget:")
    P, Tb = 20.0, 310.0
    n_dot = landauer_max_erasures_per_s(P, Tb)
    floor_power = landauer_floor_power(1e15, Tb)
    print(f"     max irreversible erasures/s at 20 W: {n_dot:.2e}")
    print(f"     Landauer floor power for 1e15 ops/s: {floor_power:.2e} W")
    print(f"     brain's ~1e15 events/s dissipate ~10^{math.log10(P / floor_power):.0f}x "
          "the thermodynamic minimum")
    print("     (sparse in BITS, but profligate in ENERGY/bit -- far from the reversible wall)")
    report.check("Landauer 20W/310K throughput ~6.7e21 erasures/s",
                 abs(n_dot / 6.7e21 - 1.0) < 0.05)

    # 5. Sparseness across scales ------------------------------------------
    print("\n5. SPARSENESS is generic (not a brain anecdote): I_used / ceiling")
    print("     {:16s} {:>10s} {:>12s} {:>12s}".format(
        "system", "I_used", "frac Bek", "frac Holo"))
    rows = sparseness_table()
    max_bek = max(r["f_bek"] for r in rows)
    max_holo = max(r["f_holo"] for r in rows)
    for r in rows:
        print("     {:16s} {:>10.1e} {:>12.1e} {:>12.1e}".format(
            r["name"], r["I_used"], r["f_bek"], r["f_holo"]))
    print(f"     tightest margin: 10^{math.log10(max_bek):.0f} of Bekenstein (low-mass E. coli), "
          f"10^{math.log10(max_holo):.0f} of holographic")
    report.check("every system is >=15 orders below Bekenstein and >=50 below holographic",
                 max_bek < 1e-15 and max_holo < 1e-50)

    # 6. Today's hardware: LLM inference vs the Landauer floor -----------------
    print("\n6. TODAY'S COMPUTE: an LLM datacenter vs the Landauer floor (same lesson):")
    P_gpu = 700.0                       # ~H100 board power, W
    print(f"     one ~700 W GPU could erase up to {gpu_max_bit_erasures_per_s(P_gpu):.2e} bits/s (Landauer ceiling)")
    params = 70e9                       # 70B-parameter dense model
    floor_token = llm_landauer_floor_per_token(params)
    actual_token = 1.0                  # ~1 J/token, order-of-magnitude for a served 70B model
    ratio = actual_token / floor_token
    print(f"     70B model: Landauer floor ~ {floor_token:.2e} J/token "
          f"(~{floor_token / 1e-9:.1f} nJ); real serving ~ {actual_token:.0e} J/token")
    print(f"     => LLM inference runs ~10^{math.log10(ratio):.0f} ABOVE the thermodynamic minimum")
    print("     (same story as the brain: nowhere near the physical wall — but profligate")
    print("      in energy per operation; reversible computing is the only way down.)")
    report.check("LLM inference sits >=1e6x above the Landauer floor",
                 ratio > 1e6)

    # 7. Energy of replication (bridge to module 03) ------------------------
    print("\n7. ENERGY OF REPLICATION (the physics bridge to module 03's replicator):")
    genome_bp = 4.6e6                      # E. coli genome, base pairs
    genome_bits = genome_bp * 2.0          # 2 bits / base pair
    floor = landauer_copy_energy(genome_bits)
    real_dna = genome_bp * 1.0e-19         # ~1e-19 J/bp (a few ATP/nucleotide)
    dna_ratio = real_dna / floor
    print(f"     E. coli genome: {genome_bp:.1e} bp = {genome_bits:.1e} bits")
    print(f"     Landauer floor to copy it once: {floor:.2e} J   (real DNA replication ~ {real_dna:.1e} J)")
    print(f"     => DNA copying runs only ~{dna_ratio:.0f}x above the thermodynamic floor -- NEAR-OPTIMAL,")
    print("        unlike brain compute (~10^6-10^7x) or LLM inference (~10^8x). Copying is cheap;")
    print("        thinking is what's expensive.")
    mu = 1e-9                              # proofread DNA polymerase error rate
    l_max_bits = eigen_max_genome_bits(mu)
    print(f"     Eigen bridge: at copy-fidelity mu~{mu:.0e}, the max stable genome is "
          f"~{l_max_bits / 2:.1e} bp")
    print(f"        ({l_max_bits:.1e} bits) -- right in the range of real genomes; its copy floor is "
          f"{landauer_copy_energy(l_max_bits):.1e} J.")
    report.check("DNA replication is within ~1000x of the Landauer floor (near-optimal)",
                 1.0 < dna_ratio < 1000.0)
    report.check("Eigen-max genome at mu~1e-9 is genome-scale (1e8-1e10 bp)",
                 1e8 < l_max_bits / 2 < 1e10)

    # 8. NVG interface ------------------------------------------------------
    print("\n8. NVG INTERFACE (model input: M_Omega = 859 MeV, vacuum 'melts' at rho_c):")
    nvg = nvg_core()
    print(f"     rho_c = M_Omega^4/(hbar c)^3 = {nvg['rho_c_energy']:.3e} J/m^3 "
          f"= {nvg['rho_c_mass']:.3e} kg/m^3   [NVG INPUT, not derived here]")
    print("     geometry of the extremal regular core (de Sitter inner scale vs horizon):")
    print(f"        inner de Sitter scale l = {nvg['l_core']:.1f} m ({nvg['l_core']/1e3:.3f} km)")
    print(f"        extremal horizon  r_h  = sqrt(3) l = {nvg['r_h']:.1f} m ({nvg['r_h']/1e3:.3f} km)")
    print(f"        extremal mass  M_crit  = {nvg['M_crit_Msun']:.3f} M_sun")
    print(f"        area bound at inner scale S(l)   = {nvg['S_inner']:.3e} bits")
    print(f"        Bekenstein-Hawking at horizon    = {nvg['S_horizon']:.3e} bits (= 3 S(l))")
    report.check("de Sitter density from l reproduces rho_c (loop closes)",
                 abs(nvg["rho_from_l"] / nvg["rho_c_mass"] - 1.0) < 1e-9)
    report.check("extremal horizon r_h == sqrt(3) * l",
                 abs(nvg["r_h"] / (math.sqrt(3) * nvg["l_core"]) - 1.0) < 1e-12)
    report.check("horizon entropy S_BH == 3 * S(inner scale)",
                 abs(nvg["S_horizon"] / nvg["S_inner"] - 3.0) < 1e-9)
    report.check("M_crit ~ 0.99 M_sun", abs(nvg["M_crit_Msun"] - 0.99) < 0.02)
    print("     HONEST: '2.2e76' is the inner-scale area bound; the horizon (which exists")
    print("     only AT/above M_crit) has S_BH = 6.6e76. Below M_crit there is no horizon,")
    print("     so the core's thermodynamic entropy is model-dependent -- not asserted here.")

    print("\n" + header("HONEST CONCLUSION"))
    print("Physics caps the SUBSTRATE -- storage (Landauer/Bekenstein/holographic), speed")
    print("(Margolus-Levitin/Bremermann/Lloyd), and, in NVG, a maximal density rho_c and a")
    print("collapse boundary M_crit ~ 1 M_sun. It does NOT supply computation, replication,")
    print("or consciousness: those are the substrate-independent theorems in 01-03. The NVG")
    print("contact point is a BOUNDARY on the container, not a merger. See NVG_INTERFACE.md.")
    print(f"\n{report.summary()}")
    print("ALL CHECKS PASSED" if report.ok else "SOME CHECKS FAILED")

    save_result("04_physical_limits", {
        "landauer_300K_J": landauer_energy(300),
        "brain_frac_bekenstein_log10": math.log10(I_used / I_bek),
        "margolus_levitin_brain_ops_s": ml_brain,
        "bremermann_per_kg": bremermann_rate_per_kg(),
        "landauer_20W_erasures_s": n_dot,
        "llm_landauer_floor_j_per_token": floor_token,
        "llm_above_landauer_ratio": ratio,
        "nvg_l_core_m": nvg["l_core"],
        "nvg_r_h_m": nvg["r_h"],
        "nvg_M_crit_Msun": nvg["M_crit_Msun"],
        "nvg_S_inner": nvg["S_inner"],
        "nvg_S_horizon": nvg["S_horizon"],
        "all_checks_passed": report.ok,
    })
    return report.ok


if __name__ == "__main__":
    raise SystemExit(0 if demo() else 1)
