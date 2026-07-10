"""Tests for module 04 -- physical ceilings & the NVG interface."""

import math

import pytest

from complife import physical_limits as pl
from complife.common import C


def test_landauer_room_temperature():
    assert pl.landauer_energy(300) == pytest.approx(2.871e-21, rel=1e-3)


def test_bekenstein_and_holographic_positive_and_ordered():
    R, M = 0.08, 1.4
    bek = pl.bekenstein_bits(R, M * C**2)
    holo = pl.holographic_bits(R)
    assert bek > 0 and holo > 0
    assert holo > bek                      # holographic is the looser bound here
    assert bek == pytest.approx(2.89e42, rel=1e-2)


def test_speed_ceilings():
    E = 1.4 * C**2
    assert pl.margolus_levitin_rate(E) == pytest.approx(7.6e50, rel=2e-2)
    assert pl.bremermann_rate_per_kg() == pytest.approx(1.356e50, rel=1e-2)
    assert pl.lloyd_ultimate_laptop(1.0) == pytest.approx(5.43e50, rel=2e-2)


def test_landauer_throughput_and_floor_inverse():
    P, T = 20.0, 310.0
    rate = pl.landauer_max_erasures_per_s(P, T)
    assert rate == pytest.approx(6.7e21, rel=5e-2)
    assert pl.landauer_floor_power(rate, T) == pytest.approx(P, rel=1e-9)


def test_nvg_core_geometry_consistent():
    nvg = pl.nvg_core()
    # de Sitter density from l reproduces rho_c (loop closes).
    assert nvg["rho_from_l"] == pytest.approx(nvg["rho_c_mass"], rel=1e-9)
    # extremal horizon r_h = sqrt(3) * l, and S_BH = 3 * S(inner scale).
    assert nvg["r_h"] == pytest.approx(math.sqrt(3) * nvg["l_core"], rel=1e-12)
    assert nvg["S_horizon"] == pytest.approx(3 * nvg["S_inner"], rel=1e-9)
    assert nvg["M_crit_Msun"] == pytest.approx(0.99, abs=0.02)
    assert nvg["l_core"] == pytest.approx(1128.0, rel=1e-2)
    assert nvg["S_inner"] == pytest.approx(2.2e76, rel=1e-2)
    assert nvg["S_horizon"] == pytest.approx(6.6e76, rel=1e-2)


def test_sparseness_all_below_ceiling():
    rows = pl.sparseness_table()
    assert all(r["f_bek"] < 1e-15 for r in rows)
    assert all(r["f_holo"] < 1e-50 for r in rows)


def test_llm_inference_far_above_landauer_floor():
    floor = pl.llm_landauer_floor_per_token(70e9)
    assert floor == pytest.approx(7.5e-9, rel=0.2)     # ~7.5 nJ/token
    ratio = 1.0 / floor                                # ~1 J/token served
    assert ratio > 1e6                                 # >6 orders above the floor
    assert math.log10(ratio) == pytest.approx(8.0, abs=0.5)


def test_gpu_erasure_ceiling_positive():
    assert pl.gpu_max_bit_erasures_per_s(700.0) > 1e22


def test_dna_replication_near_landauer_floor():
    # E. coli genome copy: near-optimal (~10-100x the floor), unlike computation.
    genome_bits = 4.6e6 * 2.0
    floor = pl.landauer_copy_energy(genome_bits)
    assert floor == pytest.approx(2.73e-14, rel=0.1)
    real_dna = 4.6e6 * 1.0e-19
    assert 1.0 < real_dna / floor < 1000.0


def test_eigen_max_genome_is_genome_scale():
    # copy fidelity mu ~ 1e-9 caps the stable genome at ~1e9 bp (real range).
    bits = pl.eigen_max_genome_bits(1e-9)
    assert 1e8 < bits / 2 < 1e10
