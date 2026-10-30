"""Tests for factor-base coverage and Lemma 9 & 10 validation (Task T09)."""

from __future__ import annotations

import random
from src.btn.ec.curve import Point, find_prime_order_curve
from src.btn.factor_base import (
    LinearHash,
    encode_point,
    estimate_coverage,
    next_prime,
    sample_factor_bases,
)


def test_next_prime() -> None:
    assert next_prime(10) == 11
    assert next_prime(11) == 13
    assert next_prime(218) == 223
    assert next_prime(1) == 2


def test_point_encoding_injective() -> None:
    curve, _ = find_prime_order_curve(109, 250)
    pts = curve.points()
    encodings = [encode_point(pt, curve.p) for pt in pts]
    assert len(encodings) == len(set(encodings)), "point encodings must be strictly distinct"
    assert all(0 <= e < 2 * curve.p for e in encodings), "encoding must be in [0, 2p - 1]"


def test_lemma_9_membership_prob() -> None:
    """Verify Lemma 9: Pr[A in F_i] = tau / s and pairwise probability <= (tau/s)^2."""
    curve, _ = find_prime_order_curve(109, 250)
    p = curve.p
    s = next_prime(2 * p)  # 223
    tau = 45
    rho = tau / s

    pts = curve.points()
    ptA, ptB = pts[0], pts[1]
    encA = encode_point(ptA, p)
    encB = encode_point(ptB, p)

    rng = random.Random(12345)
    trials = 5000
    in_A = 0
    in_both = 0

    for _ in range(trials):
        alpha = rng.randint(1, s - 1)
        beta = rng.randint(0, s - 1)
        h = LinearHash(alpha, beta, s)
        hA = h(encA) < tau
        hB = h(encB) < tau
        if hA:
            in_A += 1
        if hA and hB:
            in_both += 1

    p_A = in_A / trials
    p_both = in_both / trials
    exact_both = (tau * (tau - 1)) / (s * (s - 1))

    # Check empirical matches theoretical within statistical tolerance (3 standard deviations)
    assert abs(p_A - rho) < 0.025, f"Pr[A in Fi]={p_A:.4f} expected rho={rho:.4f}"
    assert abs(p_both - exact_both) < 0.015, f"Pr[A,B in Fi]={p_both:.4f} expected {exact_both:.4f}"
    assert p_both <= (rho ** 2) + 0.01


def test_lemma_10_coverage_bound() -> None:
    """Verify Lemma 10: when L >= max(r^{1/m}, 10m) and r >= 100, coverage >= 2/5 (0.40)."""
    # Curve order r = 127 >= 100
    curve, gen = find_prime_order_curve(109, 250)
    r = curve.order()
    m = 2
    target = gen  # arbitrary non-infinity target

    # tau = 40 gives L = 126 * 40 / 223 = 22.60 >= max(sqrt(127)=11.27, 20)
    result = estimate_coverage(curve, target, m=m, tau=40, trials=250, seed=42)

    assert result.hypothesis_met, "Lemma 10 hypotheses must be satisfied"
    assert result.trials >= 200, "Task T09 requires at least 200 trials"
    assert result.empirical_rate >= 0.40, f"Empirical rate {result.empirical_rate:.4f} must be >= 0.40"
    # Even the conservative Wilson 95% lower confidence bound should clear 0.40
    assert result.ci_lower >= 0.40, f"CI lower bound {result.ci_lower:.4f} should clear 0.40"
