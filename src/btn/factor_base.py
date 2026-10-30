r"""Factor-base constructions and decomposition coverage experiments (Lemma 9 & 10).

This module implements the pairwise-independent linear hash family factor bases
described in Section 3.2 (Lemmas 9 and 10) of 'A Subexponential Time Algorithm
for Elliptic Curve Discrete Logarithm' (v0.2, 29 October 2026):

1. For a curve E(F_p) of prime order r, choose a prime s > 2p.
2. Canonical point encoding: for affine point A = (x, y) != O:
      enc(A) = x + p * (y mod 2) in [0, 2p - 1].
3. Hash family H_i(z) = (alpha_i * z + beta_i) mod s with alpha_i in F_s*, beta_i in F_s.
4. Factor base: F_i = {A in G \ {O} : H_i(enc(A)) < tau}.
5. Under L = (r - 1) * tau / s >= max(r^{1/m}, 10m), Lemma 10 guarantees that for
   every target R in G, Pr[R = A_1 + ... + A_m for A_i in F_i] >= 2/5 = 0.40.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Sequence

from .ec.curve import Curve, Point, is_prime

__all__ = [
    "next_prime",
    "encode_point",
    "LinearHash",
    "FactorBase",
    "sample_factor_bases",
    "check_decomposition",
    "estimate_coverage",
    "CoverageTrialResult",
]


def next_prime(n: int) -> int:
    """Return the smallest prime strictly greater than ``n``."""
    candidate = n + 1 if (n % 2 == 0 or n < 2) else n + 2
    if n < 2:
        return 2
    while not is_prime(candidate):
        candidate += 2
    return candidate


def encode_point(pt: Point, p: int) -> int:
    """Encode an affine curve point into an integer in ``[0, 2p - 1]``.

    Formula: ``enc(A) = x + p * (y mod 2)``.
    Raises ``ValueError`` if ``pt`` is the point at infinity.
    """
    if pt.is_infinity or pt.x is None or pt.y is None:
        raise ValueError("cannot encode the point at infinity")
    return pt.x + p * (pt.y % 2)


@dataclass(frozen=True)
class LinearHash:
    """A linear hash function ``H(z) = (alpha * z + beta) mod s`` over F_s."""

    alpha: int
    beta: int
    s: int

    def __post_init__(self) -> None:
        if not (1 <= self.alpha < self.s):
            raise ValueError("alpha must be in [1, s - 1]")
        if not (0 <= self.beta < self.s):
            raise ValueError("beta must be in [0, s - 1]")

    def __call__(self, z: int) -> int:
        return (self.alpha * z + self.beta) % self.s


@dataclass(frozen=True)
class FactorBase:
    """A factor base F_i defined by a hash function H_i and threshold tau.

    A finite point A is in F_i if and only if ``H_i(enc(A)) < tau``.
    """

    h: LinearHash
    tau: int
    p: int
    points: tuple[Point, ...]

    @classmethod
    def from_curve(
        cls,
        curve: Curve,
        h: LinearHash,
        tau: int,
    ) -> FactorBase:
        p = curve.p
        affine = curve.points()
        filtered = tuple(pt for pt in affine if h(encode_point(pt, p)) < tau)
        return cls(h=h, tau=tau, p=p, points=filtered)

    def contains(self, pt: Point) -> bool:
        if pt.is_infinity or pt.x is None or pt.y is None:
            return False
        return self.h(encode_point(pt, self.p)) < self.tau

    def __len__(self) -> int:
        return len(self.points)


def sample_factor_bases(
    curve: Curve,
    m: int,
    tau: int,
    s: int,
    rng: random.Random,
) -> list[FactorBase]:
    """Sample ``m`` independent random factor bases according to Section 3.2."""
    bases: list[FactorBase] = []
    affine = curve.points()
    p = curve.p
    for _ in range(m):
        alpha = rng.randint(1, s - 1)
        beta = rng.randint(0, s - 1)
        h = LinearHash(alpha=alpha, beta=beta, s=s)
        pts = tuple(pt for pt in affine if h(encode_point(pt, p)) < tau)
        bases.append(FactorBase(h=h, tau=tau, p=p, points=pts))
    return bases


def check_decomposition(
    curve: Curve,
    factor_bases: Sequence[FactorBase],
    target: Point,
) -> bool:
    """Check whether ``target`` decomposes as ``A_1 + ... + A_m`` with ``A_i in F_i``.

    For m=2, this runs in time O(|F_1|).
    For m=3, this runs in time O(|F_1| * |F_2|).
    """
    m = len(factor_bases)
    if m == 1:
        return factor_bases[0].contains(target)

    if m == 2:
        fb1, fb2 = factor_bases[0], factor_bases[1]
        fb2_set = set(fb2.points)
        for a1 in fb1.points:
            need_a2 = curve.add(target, curve.neg(a1))
            if need_a2 in fb2_set:
                return True
        return False

    if m == 3:
        fb1, fb2, fb3 = factor_bases[0], factor_bases[1], factor_bases[2]
        fb3_set = set(fb3.points)
        for a1 in fb1.points:
            t_minus_a1 = curve.add(target, curve.neg(a1))
            for a2 in fb2.points:
                need_a3 = curve.add(t_minus_a1, curve.neg(a2))
                if need_a3 in fb3_set:
                    return True
        return False

    raise NotImplementedError(f"decomposition check for m={m} not implemented in toy verifier")


@dataclass(frozen=True)
class CoverageTrialResult:
    r: int
    p: int
    m: int
    s: int
    tau: int
    L: float
    hypothesis_met: bool
    trials: int
    successes: int
    empirical_rate: float
    ci_lower: float
    ci_upper: float


def wilson_score_interval(successes: int, n: int, confidence: float = 0.95) -> tuple[float, float]:
    """Compute the Wilson score confidence interval for a binomial proportion."""
    if n == 0:
        return 0.0, 1.0
    # For 95% confidence, z = 1.95996
    z = 1.959963984540054 if abs(confidence - 0.95) < 1e-4 else 1.96
    p_hat = successes / n
    denom = 1 + z**2 / n
    centre = (p_hat + z**2 / (2 * n)) / denom
    margin = (z * math.sqrt((p_hat * (1 - p_hat) + z**2 / (4 * n)) / n)) / denom
    return max(0.0, centre - margin), min(1.0, centre + margin)


def estimate_coverage(
    curve: Curve,
    target: Point,
    *,
    m: int = 2,
    tau: int,
    trials: int = 200,
    seed: int = 0,
) -> CoverageTrialResult:
    """Run coverage trials and estimate decomposition probability under random hash seeds."""
    p = curve.p
    r = curve.order()
    n = r - 1
    s = next_prime(2 * p)
    L = n * (tau / s)
    threshold = max(r ** (1 / m), 10 * m)
    hyp_met = (r >= 100) and (m >= 2) and (L >= threshold)

    rng = random.Random(seed)
    successes = 0

    for _ in range(trials):
        bases = sample_factor_bases(curve, m, tau, s, rng)
        if check_decomposition(curve, bases, target):
            successes += 1

    rate = successes / trials
    ci_low, ci_high = wilson_score_interval(successes, trials, 0.95)

    return CoverageTrialResult(
        r=r,
        p=p,
        m=m,
        s=s,
        tau=tau,
        L=L,
        hypothesis_met=hyp_met,
        trials=trials,
        successes=successes,
        empirical_rate=rate,
        ci_lower=ci_low,
        ci_upper=ci_high,
    )
