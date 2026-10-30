"""A one-vertex semantic encoding for an arbitrary finite language.

This is a correctness oracle, not a low-degree construction.  A language
``L ⊆ {0,1}^m`` is encoded by a single vertex with all ``m`` bits as interface
edges.  The encoding is parsimonious for trivial reasons: there are no
auxiliary edges, so each word has exactly one extension (itself) iff it is in
``L``.  The degree is ``m``, which is far above the paper's ``O(s^{9/10})``
requirement at scale.
"""

from __future__ import annotations

from typing import Callable, Sequence

from ..network import BTN, Predicate, Vertex


def lookup_btn(num_bits: int, predicate: Predicate) -> BTN:
    """Encode ``{w in {0,1}^num_bits : predicate(w)}`` with one vertex."""
    if num_bits < 0:
        raise ValueError("num_bits must be non-negative")
    edges = tuple(range(num_bits))
    return BTN(
        n_edges=num_bits,
        vertices=(Vertex(edges, predicate),),
        interface=edges,
    )


def word_from_bits(bits: Sequence[bool]) -> tuple[bool, ...]:
    return tuple(bool(bit) for bit in bits)


def lookup_accepts(btn: BTN, word: Sequence[bool]) -> bool:
    """Evaluate a lookup encoding on a complete interface word."""
    if len(word) != btn.n_edges:
        raise ValueError("word length does not match the encoding")
    return btn.accepts(tuple(bool(bit) for bit in word))


__all__ = ["lookup_btn", "lookup_accepts", "word_from_bits", "Callable"]
