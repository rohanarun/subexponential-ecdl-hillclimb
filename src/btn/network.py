"""Exact Boolean tensor network (BTN) semantics.

A BTN is a multigraph whose edges carry bits and whose vertices carry Boolean
predicates over their incident edges.  ``Contract(BTN)`` is the number of edge
assignments satisfying every vertex predicate (Definition 1 of the paper).

This module is deliberately small and literal.  It is the semantic oracle used
by the tests; it is not an implementation of the paper's tensor contraction
algorithm, which is the external Theorem D.1.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Callable, Iterable, Mapping, Sequence

Predicate = Callable[[tuple[bool, ...]], bool]
Assignment = tuple[bool, ...]


@dataclass(frozen=True)
class Vertex:
    """A predicate applied to an ordered list of incident edge indices."""

    edges: tuple[int, ...]
    predicate: Predicate

    def satisfied(self, assignment: Sequence[bool]) -> bool:
        return bool(self.predicate(tuple(bool(assignment[e]) for e in self.edges)))


@dataclass(frozen=True)
class BTN:
    """A Boolean tensor network with ordered edges and vertices."""

    n_edges: int
    vertices: tuple[Vertex, ...]
    interface: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        if self.n_edges < 0:
            raise ValueError("n_edges must be non-negative")
        for vertex in self.vertices:
            for edge in vertex.edges:
                if not 0 <= edge < self.n_edges:
                    raise ValueError(f"vertex references edge {edge}, n_edges={self.n_edges}")
        if len(set(self.interface)) != len(self.interface):
            raise ValueError("interface edges must be distinct")
        for edge in self.interface:
            if not 0 <= edge < self.n_edges:
                raise ValueError(f"interface references edge {edge}, n_edges={self.n_edges}")

    def accepts(self, assignment: Sequence[bool]) -> bool:
        if len(assignment) != self.n_edges:
            raise ValueError(f"expected {self.n_edges} bits, got {len(assignment)}")
        return all(vertex.satisfied(assignment) for vertex in self.vertices)

    def satisfying_assignments(self) -> Iterable[Assignment]:
        if self.n_edges > 22:
            raise ValueError("brute-force enumeration is limited to 22 edges")
        for bits in product((False, True), repeat=self.n_edges):
            if self.accepts(bits):
                yield bits

    def contract(self) -> int:
        """Return ``Contract(BTN)`` by exhaustive enumeration."""
        return sum(1 for _ in self.satisfying_assignments())

    def count_extensions(self, fixed: Mapping[int, bool]) -> int:
        """Count satisfying assignments that agree with ``fixed`` on those edges.

        Only the free edges are enumerated, so this is practical for networks
        with many interface bits and few auxiliary bits.
        """
        fixed = {int(edge): bool(bit) for edge, bit in fixed.items()}
        for edge in fixed:
            if not 0 <= edge < self.n_edges:
                raise ValueError(f"fixed edge {edge} out of range")
        free = [edge for edge in range(self.n_edges) if edge not in fixed]
        if len(free) > 24:
            raise ValueError("too many free edges for exhaustive extension counting")
        count = 0
        for bits in product((False, True), repeat=len(free)):
            assignment = [False] * self.n_edges
            for edge, bit in fixed.items():
                assignment[edge] = bit
            for edge, bit in zip(free, bits):
                assignment[edge] = bit
            if self.accepts(assignment):
                count += 1
        return count

    def interface_word(self, assignment: Sequence[bool]) -> tuple[bool, ...]:
        return tuple(bool(assignment[edge]) for edge in self.interface)


def check_parsimony(
    btn: BTN,
    language: Iterable[Sequence[bool]],
    all_words: Iterable[Sequence[bool]] | None = None,
    word_edges: Sequence[int] | None = None,
) -> list[tuple[tuple[bool, ...], int, int]]:
    """Check that ``btn`` parsimoniously encodes ``language``.

    Returns a list of ``(word, observed_extensions, expected_extensions)`` for
    every mismatch.  An empty list means the check passed.

    ``word_edges`` defaults to ``btn.interface``.  If ``all_words`` is omitted,
    every bit string of the appropriate length is checked.
    """
    edges = tuple(btn.interface if word_edges is None else word_edges)
    language_set = {tuple(bool(bit) for bit in word) for word in language}
    if all_words is None:
        all_words = product((False, True), repeat=len(edges))
    failures: list[tuple[tuple[bool, ...], int, int]] = []
    for word in all_words:
        word = tuple(bool(bit) for bit in word)
        if len(word) != len(edges):
            raise ValueError("word length does not match the interface")
        observed = btn.count_extensions({edge: bit for edge, bit in zip(edges, word)})
        expected = 1 if word in language_set else 0
        if observed != expected:
            failures.append((word, observed, expected))
    return failures
