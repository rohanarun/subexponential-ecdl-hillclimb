"""Small prime-field elliptic curves for toy experiments.

Only short-Weierstrass curves over prime fields are supported.  The arithmetic
is straightforward affine arithmetic with modular inverses; it is intended for
``p`` small enough to enumerate points, not for cryptography.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

__all__ = [
    "Point",
    "Curve",
    "INFINITY",
    "is_prime",
    "count_points",
    "find_prime_order_curve",
]


@dataclass(frozen=True, order=True)
class Point:
    """An affine point, or ``INFINITY`` when both coordinates are ``None``."""

    x: int | None
    y: int | None

    @property
    def is_infinity(self) -> bool:
        return self.x is None and self.y is None

    def __post_init__(self) -> None:
        if (self.x is None) != (self.y is None):
            raise ValueError("a point must have both coordinates or neither")


INFINITY = Point(None, None)


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    divisor = 3
    while divisor * divisor <= n:
        if n % divisor == 0:
            return False
        divisor += 2
    return True


@dataclass(frozen=True)
class Curve:
    """``y^2 = x^3 + a x + b`` over ``F_p``."""

    p: int
    a: int
    b: int

    def __post_init__(self) -> None:
        if self.p <= 3 or not is_prime(self.p):
            raise ValueError("p must be an odd prime greater than 3")
        if (4 * self.a**3 + 27 * self.b**2) % self.p == 0:
            raise ValueError("singular curve: 4a^3 + 27b^2 = 0 mod p")

    def on_curve(self, point: Point) -> bool:
        if point.is_infinity:
            return True
        assert point.x is not None and point.y is not None
        return (point.y * point.y - (point.x**3 + self.a * point.x + self.b)) % self.p == 0

    def neg(self, point: Point) -> Point:
        if point.is_infinity:
            return point
        assert point.x is not None and point.y is not None
        return Point(point.x, (-point.y) % self.p)

    def add(self, left: Point, right: Point) -> Point:
        if left.is_infinity:
            return right
        if right.is_infinity:
            return left
        assert left.x is not None and left.y is not None
        assert right.x is not None and right.y is not None
        p = self.p
        if left.x == right.x and (left.y + right.y) % p == 0:
            return INFINITY
        if left == right:
            if left.y == 0:
                return INFINITY
            slope = (3 * left.x * left.x + self.a) * pow(2 * left.y, -1, p) % p
        else:
            slope = (right.y - left.y) * pow(right.x - left.x, -1, p) % p
        x3 = (slope * slope - left.x - right.x) % p
        y3 = (slope * (left.x - x3) - left.y) % p
        return Point(x3, y3)

    def mul(self, scalar: int, point: Point) -> Point:
        if scalar < 0:
            return self.mul(-scalar, self.neg(point))
        result = INFINITY
        addend = point
        while scalar:
            if scalar & 1:
                result = self.add(result, addend)
            addend = self.add(addend, addend)
            scalar >>= 1
        return result

    def points(self) -> list[Point]:
        """All affine points, excluding infinity."""
        result: list[Point] = []
        for x in range(self.p):
            rhs = (x * x * x + self.a * x + self.b) % self.p
            for y in range(self.p):
                if (y * y - rhs) % self.p == 0:
                    result.append(Point(x, y))
        return result

    def order(self) -> int:
        """Group order including infinity, by enumeration."""
        return len(self.points()) + 1

    def is_prime_order(self) -> bool:
        return is_prime(self.order())


def count_points(p: int, a: int, b: int) -> int:
    return Curve(p, a, b).order()


def find_prime_order_curve(
    p_min: int = 101,
    p_max: int = 200,
    a_max: int = 12,
    b_max: int = 12,
) -> tuple[Curve, Point]:
    """Find a nonsingular curve with prime group order and a generator.

    Returns ``(curve, generator)``.  The search is intentionally tiny and is
    used only to make toy examples reproducible.
    """
    for p in range(max(5, p_min), p_max + 1):
        if not is_prime(p):
            continue
        for a in range(1, a_max + 1):
            for b in range(1, b_max + 1):
                if (4 * a**3 + 27 * b**2) % p == 0:
                    continue
                curve = Curve(p, a, b)
                order = curve.order()
                if not is_prime(order):
                    continue
                points = curve.points()
                if not points:
                    continue
                generator = points[0]
                if curve.mul(order, generator) == INFINITY:
                    return curve, generator
    raise RuntimeError("no prime-order toy curve found in the requested range")


def iter_multiples(curve: Curve, generator: Point) -> Iterator[Point]:
    """Yield ``[k]P`` for ``k = 0, 1, ...`` until the point repeats."""
    seen: set[Point] = set()
    point = INFINITY
    while point not in seen:
        seen.add(point)
        yield point
        point = curve.add(point, generator)
