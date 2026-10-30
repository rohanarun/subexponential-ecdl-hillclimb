"""Toy index calculus for prime-order elliptic curves.

This implements the *shape* of the paper's reduction at toy scale:

1. choose random factor bases ``F_1, ..., F_m``;
2. collect relations ``[u]P + [v]Q = A_1 + ... + A_m``;
3. find a linear combination of relations that eliminates the factor-base
   columns;
4. recover ``xi`` from the remaining ``P`` and ``Q`` coefficients.

The decomposition step is an exhaustive search over the toy factor bases, not a
Boolean tensor contraction.  The point is to validate the algebra and the
relation-collection interface, not the paper's asymptotic claim.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Sequence

from .ec.curve import INFINITY, Curve, Point
from .linalg import left_nullspace

__all__ = ["ECDLResult", "toy_index_calculus", "demo"]


@dataclass(frozen=True)
class ECDLResult:
    success: bool
    xi: int | None
    attempts: int
    relations: int
    n_slots: int
    factor_base_sizes: tuple[int, ...]
    reason: str


def _find_decomposition(
    curve: Curve,
    factor_bases: Sequence[Sequence[Point]],
    target: Point,
) -> tuple[Point, ...] | None:
    """Find ``A_i in F_i`` with ``A_1 + ... + A_m = target``, or ``None``."""
    if not factor_bases:
        return () if target.is_infinity else None
    if len(factor_bases) == 1:
        return (target,) if target in set(factor_bases[0]) else None
    if len(factor_bases) == 2:
        second = set(factor_bases[1])
        for first in factor_bases[0]:
            needed = curve.add(target, curve.neg(first))
            if needed in second:
                return (first, needed)
        return None

    last = set(factor_bases[-1])
    prefix = factor_bases[:-1]

    def search(index: int, remaining: Point, chosen: tuple[Point, ...]) -> tuple[Point, ...] | None:
        if index == len(prefix):
            return chosen + (remaining,) if remaining in last else None
        for point in prefix[index]:
            rest = search(index + 1, curve.add(remaining, curve.neg(point)), chosen + (point,))
            if rest is not None:
                return rest
        return None

    return search(0, target, ())


def _relation_row(
    factor_bases: Sequence[Sequence[Point]],
    decomposition: Sequence[Point],
    u: int,
    v: int,
    order: int,
) -> list[int]:
    n_slots = sum(len(factor_base) for factor_base in factor_bases)
    row = [0] * (n_slots + 2)
    offset = 0
    for factor_base, chosen in zip(factor_bases, decomposition):
        row[offset + factor_base.index(chosen)] = -1 % order
        offset += len(factor_base)
    row[n_slots] = u % order
    row[n_slots + 1] = v % order
    return row


def _extract(
    rows: Sequence[Sequence[int]],
    n_slots: int,
    order: int,
) -> tuple[int | None, str]:
    """Return ``(xi, reason)`` from relation rows, or ``(None, reason)``."""
    matrix = [list(row[:n_slots]) for row in rows]
    for combination in left_nullspace(matrix, order):
        u = sum(coefficient * row[n_slots] for coefficient, row in zip(combination, rows)) % order
        v = sum(coefficient * row[n_slots + 1] for coefficient, row in zip(combination, rows)) % order
        if v % order:
            return (-u * pow(v, -1, order)) % order, "ok"
    return None, "all null combinations have zero Q coefficient"


def toy_index_calculus(
    curve: Curve,
    generator: Point,
    target: Point,
    *,
    m: int = 2,
    factor_base_size: int | None = None,
    seed: int = 0,
    max_attempts: int = 100_000,
) -> ECDLResult:
    """Recover ``xi`` with ``target = [xi] generator`` on a toy curve."""
    order = curve.order()
    if not curve.is_prime_order():
        raise ValueError("this toy implementation expects a prime-order curve")
    if generator.is_infinity or not curve.on_curve(generator):
        raise ValueError("generator must be a finite point on the curve")
    if target.is_infinity or not curve.on_curve(target):
        raise ValueError("target must be a finite point on the curve")
    if m < 1:
        raise ValueError("m must be at least 1")

    affine = curve.points()
    size = factor_base_size or math.ceil(order ** (1 / m))
    if size < 1 or size > len(affine):
        raise ValueError("factor base size is out of range")

    rng = random.Random(seed)
    factor_bases = [rng.sample(affine, size) for _ in range(m)]
    n_slots = sum(len(factor_base) for factor_base in factor_bases)
    rows: list[list[int]] = []
    attempts = 0

    while len(rows) < n_slots + 1 and attempts < max_attempts:
        attempts += 1
        u = rng.randrange(order)
        v = rng.randrange(order)
        relation_target = curve.add(curve.mul(u, generator), curve.mul(v, target))
        decomposition = _find_decomposition(curve, factor_bases, relation_target)
        if decomposition is None:
            continue
        rows.append(_relation_row(factor_bases, decomposition, u, v, order))

    if len(rows) < n_slots + 1:
        return ECDLResult(
            success=False,
            xi=None,
            attempts=attempts,
            relations=len(rows),
            n_slots=n_slots,
            factor_base_sizes=tuple(len(factor_base) for factor_base in factor_bases),
            reason="not enough relations before the attempt cap",
        )

    xi, reason = _extract(rows, n_slots, order)
    if xi is None:
        return ECDLResult(
            success=False,
            xi=None,
            attempts=attempts,
            relations=len(rows),
            n_slots=n_slots,
            factor_base_sizes=tuple(len(factor_base) for factor_base in factor_bases),
            reason=reason,
        )

    if curve.mul(xi, generator) != target:
        return ECDLResult(
            success=False,
            xi=xi,
            attempts=attempts,
            relations=len(rows),
            n_slots=n_slots,
            factor_base_sizes=tuple(len(factor_base) for factor_base in factor_bases),
            reason="extracted value does not reproduce the target",
        )

    return ECDLResult(
        success=True,
        xi=xi,
        attempts=attempts,
        relations=len(rows),
        n_slots=n_slots,
        factor_base_sizes=tuple(len(factor_base) for factor_base in factor_bases),
        reason=reason,
    )


def demo() -> None:
    """Run one reproducible toy example and print the result."""
    curve = Curve(101, 6, 9)
    generator = Point(0, 3)
    order = curve.order()
    if not curve.is_prime_order():
        raise RuntimeError("the pinned demo curve is not prime-order")
    xi = 19
    target = curve.mul(xi, generator)
    result = toy_index_calculus(curve, generator, target, m=2, seed=0)
    print(f"curve: y^2 = x^3 + {curve.a}x + {curve.b} over F_{curve.p}")
    print(f"group order: {order} (prime)")
    print(f"generator: {generator}")
    print(f"target: {target} = [{xi}]P")
    print(f"factor-base sizes: {result.factor_base_sizes}")
    print(f"relations: {result.relations} / {result.n_slots + 1} needed")
    print(f"attempts: {result.attempts}")
    print(f"recovered: {result.xi}")
    print(f"success: {result.success} ({result.reason})")
    if not result.success or result.xi != xi:
        raise SystemExit(1)


if __name__ == "__main__":
    demo()
