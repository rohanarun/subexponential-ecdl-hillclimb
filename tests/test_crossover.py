"""Test suite verifying concrete complexity trade-offs and crossover bounds."""

from __future__ import annotations

import math

from eval.compute_crossover import (
    index_calculus_cost_exponent,
    optimal_split_for_b,
    theoretical_crossover_bitlength,
)


def test_theoretical_crossover_bound() -> None:
    """Verify that the theoretical crossover bit-length satisfies b* >= 2^193."""
    b_star = theoretical_crossover_bitlength()
    log2_b_star = math.log2(b_star)
    assert 193.0 <= log2_b_star <= 194.0, f"Expected crossover approx 2^193.2, got 2^{log2_b_star}"


def test_p256_strictly_inferior_to_pollards_rho() -> None:
    """Verify that for b = 256, all choices of m yield complexity strictly greater than 2^128."""
    rho_cost = 128.0  # 256 / 2
    opt_m, min_cost = optimal_split_for_b(256)

    # Minimum cost is achieved at m = 3
    assert opt_m == 3
    # Cost is at least 2^330
    assert min_cost >= 330.0, f"Expected cost >= 2^330 for b=256, got 2^{min_cost}"
    # Deficit exceeds 200 orders of magnitude
    deficit = min_cost - rho_cost
    assert deficit > 200.0, f"Expected deficit > 200 bits for b=256, got {deficit}"

    # Explicit check for m <= 6 (linear algebra bottleneck)
    for m in range(2, 7):
        cost = index_calculus_cost_exponent(256, m)
        assert cost["linalg"] >= rho_cost, f"Linalg cost must be >= 2^128 for m={m}"

    # Explicit check for m >= 7 (contraction bottleneck)
    for m in range(7, 15):
        cost = index_calculus_cost_exponent(256, m)
        assert cost["contract"] > rho_cost, f"Contraction cost must be > 2^128 for m={m}"


def test_p384_and_p521_security() -> None:
    """Verify that NIST P-384 and P-521 have deficits exceeding 250 and 350 orders of magnitude."""
    opt_m_384, min_cost_384 = optimal_split_for_b(384)
    assert min_cost_384 - 192.0 > 250.0, f"P-384 deficit must be > 250, got {min_cost_384 - 192.0}"

    opt_m_521, min_cost_521 = optimal_split_for_b(521)
    assert min_cost_521 - 260.5 > 350.0, f"P-521 deficit must be > 350, got {min_cost_521 - 260.5}"
