"""Baseline parsimonious BTN encoding of d-bit integer multiplication.

This is a *table* construction, not the paper's Theorem 3 construction.  For
each output bit it uses one vertex connected to all input bits and that output
bit.  The result has ``4d`` edges and maximum degree ``2d + 1``, so it is linear
in edges but only ``O(d)`` in degree -- well above the paper's ``O(d^{3/4})``
bound.  It exists to pin the semantics and to give later low-degree work a
trusted oracle.
"""

from __future__ import annotations

from ..network import BTN, Vertex

__all__ = [
    "bits_to_int",
    "int_to_bits",
    "mult_table_btn",
    "mult_word",
    "product_language",
]


def bits_to_int(bits: tuple[bool, ...]) -> int:
    """Decode a little-endian bit tuple."""
    value = 0
    for index, bit in enumerate(bits):
        if bit:
            value |= 1 << index
    return value


def int_to_bits(value: int, width: int) -> tuple[bool, ...]:
    """Encode ``value`` as ``width`` little-endian bits."""
    if value < 0 or value >= 1 << width:
        raise ValueError(f"{value} does not fit in {width} bits")
    return tuple(bool((value >> index) & 1) for index in range(width))


def mult_word(a: int, b: int, d: int, z: int | None = None) -> tuple[bool, ...]:
    """Return the interface word ``(a, b, z)`` in little-endian order."""
    if z is None:
        z = a * b
    return int_to_bits(a, d) + int_to_bits(b, d) + int_to_bits(z, 2 * d)


def mult_table_btn(d: int) -> BTN:
    """Encode ``ab = z`` for d-bit ``a,b`` and 2d-bit ``z``.

    Edges 0..d-1 are ``a``, d..2d-1 are ``b``, and 2d..4d-1 are ``z``.
    The encoding is parsimonious: fixing ``a`` and ``b`` forces every ``z`` bit.
    """
    if d < 1:
        raise ValueError("d must be at least 1")
    a_edges = tuple(range(d))
    b_edges = tuple(range(d, 2 * d))
    z_edges = tuple(range(2 * d, 4 * d))
    input_edges = a_edges + b_edges

    vertices: list[Vertex] = []
    for output_index in range(2 * d):
        edges = input_edges + (z_edges[output_index],)

        def predicate(bits: tuple[bool, ...], output_index: int = output_index) -> bool:
            a = bits_to_int(bits[:d])
            b = bits_to_int(bits[d : 2 * d])
            expected = (a * b >> output_index) & 1
            return bits[2 * d] == bool(expected)

        vertices.append(Vertex(edges, predicate))

    return BTN(
        n_edges=4 * d,
        vertices=tuple(vertices),
        interface=input_edges + z_edges,
    )


def product_language(d: int) -> list[tuple[bool, ...]]:
    """All valid ``(a, b, a*b)`` words for d-bit inputs."""
    return [mult_word(a, b, d) for a in range(1 << d) for b in range(1 << d)]
