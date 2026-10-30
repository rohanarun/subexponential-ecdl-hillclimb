#!/usr/bin/env python3
"""Evaluate concrete complexity trade-offs and crossover bounds for Theorem 4."""

from __future__ import annotations

import math


def index_calculus_cost_exponent(b: int, m: int, c_contract: float = 1.0) -> dict[str, float]:
    """Calculate the concrete complexity exponents for curve bit-length ``b`` and splitting ``m``.

    Returns:
        A dict with 'linalg', 'contraction', 'total', and 'rho' exponents (in log2).
    """
    if b < 1 or m < 2:
        raise ValueError("b >= 1 and m >= 2 required")

    linalg_exp = 3.0 * b / m
    s = m * b
    log2_s = math.log2(s)
    contract_exp = b / m + c_contract * s / math.sqrt(log2_s)
    total_exp = max(linalg_exp, contract_exp)
    rho_exp = b / 2.0

    return {
        "linalg": linalg_exp,
        "contract": contract_exp,
        "total": total_exp,
        "rho": rho_exp,
        "ratio_to_rho": total_exp / rho_exp,
    }


def optimal_split_for_b(b: int, c_contract: float = 1.0) -> tuple[int, float]:
    """Find the splitting parameter ``m`` that minimizes total cost for bit-length ``b``."""
    best_m = 2
    best_cost = float("inf")
    # Search reasonable values of m
    for m in range(2, min(500, max(10, b))):
        cost = index_calculus_cost_exponent(b, m, c_contract)["total"]
        if cost < best_cost:
            best_cost = cost
            best_m = m
    return best_m, best_cost


def theoretical_crossover_bitlength() -> float:
    """Return the theoretical minimum field bit-length b where index calculus can beat 2^{b/2}.

    Requires m >= 7 (so that 3b/m < b/2), and log2(mb) > 4m^2 (so that mb/sqrt(log(mb)) < b/2).
    For m = 7: log2(7b) > 4*49 = 196 => b > 2^196 / 7 approx 2^193.2.
    """
    m = 7
    required_log2_mb = 4 * (m**2)
    return (2**required_log2_mb) / m


if __name__ == "__main__":
    print("=== Subexponential ECDL Concrete Complexity Evaluation ===")
    for b in [256, 384, 521]:
        opt_m, min_cost = optimal_split_for_b(b)
        res = index_calculus_cost_exponent(b, opt_m)
        print(
            f"b = {b:3d}: Pollard's rho = 2^{res['rho']:.1f}, "
            f"Index Calculus (opt m={opt_m}) = 2^{min_cost:.1f} "
            f"({min_cost - res['rho']:.1f} orders of 2 slower)"
        )

    crossover_b = theoretical_crossover_bitlength()
    print(f"\nTheoretical crossover lower bound: b* >= 2^{math.log2(crossover_b):.1f} bits")
