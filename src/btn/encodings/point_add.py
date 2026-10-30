"""Baseline parsimonious BTN encoding of elliptic-curve point addition.

A point is encoded as ``(infinity_flag, x bits, y bits)``.  The baseline uses a
single vertex whose predicate decodes all three points and checks
``P1 + P2 = P3``.  It is a semantic oracle with degree ``3(1 + 2b)``, not the
paper's ``O(b^{3/4})`` construction.
"""

from __future__ import annotations

from ..ec.curve import INFINITY, Curve, Point
from ..network import BTN, Vertex

__all__ = [
    "bits_per_coord",
    "encode_point",
    "decode_point",
    "point_add_btn",
    "point_word",
]


def bits_per_coord(curve: Curve) -> int:
    """Number of bits needed for a coordinate in ``[0, p)``."""
    return max(1, (curve.p - 1).bit_length())


def _int_to_bits(value: int, width: int) -> tuple[bool, ...]:
    if value < 0 or value >= 1 << width:
        raise ValueError(f"{value} does not fit in {width} bits")
    return tuple(bool((value >> index) & 1) for index in range(width))


def _bits_to_int(bits: tuple[bool, ...]) -> int:
    value = 0
    for index, bit in enumerate(bits):
        if bit:
            value |= 1 << index
    return value


def encode_point(point: Point, width: int) -> tuple[bool, ...]:
    """Encode a point as ``1 + 2*width`` bits.

    Infinity is ``(True, 0, ..., 0)``.  Affine points are
    ``(False, x bits, y bits)`` in little-endian order.
    """
    if point.is_infinity:
        return (True,) + (False,) * (2 * width)
    assert point.x is not None and point.y is not None
    return (False,) + _int_to_bits(point.x, width) + _int_to_bits(point.y, width)


def decode_point(bits: tuple[bool, ...], width: int) -> Point:
    """Decode and validate the canonical point encoding."""
    if len(bits) != 1 + 2 * width:
        raise ValueError("wrong point encoding length")
    infinity, x_bits, y_bits = bits[0], bits[1 : 1 + width], bits[1 + width :]
    x = _bits_to_int(x_bits)
    y = _bits_to_int(y_bits)
    if infinity:
        if x != 0 or y != 0:
            raise ValueError("non-canonical infinity encoding")
        return INFINITY
    return Point(x, y)


def point_word(p1: Point, p2: Point, p3: Point, width: int) -> tuple[bool, ...]:
    return encode_point(p1, width) + encode_point(p2, width) + encode_point(p3, width)


def point_add_btn(curve: Curve, width: int | None = None) -> BTN:
    """Encode ``P1 + P2 = P3`` with one vertex over all point bits."""
    if width is None:
        width = bits_per_coord(curve)
    point_bits = 1 + 2 * width
    n_edges = 3 * point_bits
    edges = tuple(range(n_edges))

    def predicate(bits: tuple[bool, ...]) -> bool:
        try:
            p1 = decode_point(bits[:point_bits], width)
            p2 = decode_point(bits[point_bits : 2 * point_bits], width)
            p3 = decode_point(bits[2 * point_bits :], width)
        except ValueError:
            return False
        for point in (p1, p2, p3):
            if point.is_infinity:
                continue
            assert point.x is not None and point.y is not None
            if point.x >= curve.p or point.y >= curve.p:
                return False
            if not curve.on_curve(point):
                return False
        return curve.add(p1, p2) == p3

    return BTN(n_edges=n_edges, vertices=(Vertex(edges, predicate),), interface=edges)
