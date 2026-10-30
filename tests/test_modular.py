"""Tests verifying Lemma 8 modular addition and multiplication networks (Task T07)."""

from __future__ import annotations

import pytest
from src.btn.encodings.integer_mult import bits_to_int, int_to_bits
from src.btn.encodings.modular import (
    mod_add_btn,
    mod_add_witness,
    mod_mult_lowdegree_btn,
    mod_mult_lowdegree_witness,
    mod_mult_table_btn,
    mod_word,
)


@pytest.mark.parametrize("q", [2, 3])
def test_mod_add_exhaustive_all_words_parsimony(q: int) -> None:
    """Verify that mod_add_btn parsimoniously encodes x + y = z mod q across all 2^{3d} words."""
    d = q.bit_length()
    btn = mod_add_btn(q, d)

    for x in range(1 << d):
        for y in range(1 << d):
            for z in range(1 << d):
                fixed = {
                    i: bit
                    for i, bit in enumerate(
                        int_to_bits(x, d) + int_to_bits(y, d) + int_to_bits(z, d)
                    )
                }
                observed = btn.count_extensions(fixed)
                expected = 1 if (x < q and y < q and z < q and (x + y) % q == z) else 0
                assert observed == expected, (
                    f"mod_add mismatch for q={q} at ({x}, {y}, {z}): got {observed}, expected {expected}"
                )


@pytest.mark.parametrize("q", [5, 7])
def test_mod_add_parsimony_and_rejection(q: int) -> None:
    """Verify parsimony on all canonical pairs and rejection of invalid and non-canonical words."""
    d = q.bit_length()
    btn = mod_add_btn(q, d)

    for x in range(q):
        for y in range(q):
            z = (x + y) % q
            fixed_valid = {
                i: bit
                for i, bit in enumerate(
                    int_to_bits(x, d) + int_to_bits(y, d) + int_to_bits(z, d)
                )
            }
            assert btn.count_extensions(fixed_valid) == 1, f"Failed for valid ({x}+{y})%{q}={z}"

            bad_z = (z + 1) % q
            fixed_invalid = {
                i: bit
                for i, bit in enumerate(
                    int_to_bits(x, d) + int_to_bits(y, d) + int_to_bits(bad_z, d)
                )
            }
            assert btn.count_extensions(fixed_invalid) == 0, f"Accepted invalid sum ({x}+{y})%{q}={bad_z}"

    # Non-canonical inputs (>= q) must have 0 extensions
    for bad_val in range(q, 1 << d):
        fixed_bad = {
            i: bit
            for i, bit in enumerate(
                int_to_bits(bad_val, d) + int_to_bits(0, d) + int_to_bits(0, d)
            )
        }
        assert btn.count_extensions(fixed_bad) == 0, f"Accepted non-canonical input {bad_val} >= {q}"


@pytest.mark.parametrize("q", [3, 5, 7, 11])
def test_mod_add_witness_acceptance_and_rejection(q: int) -> None:
    """Verify that mod_add_witness produces valid satisfying assignments."""
    d = q.bit_length()
    btn = mod_add_btn(q, d)

    for x in range(q):
        for y in range(q):
            asgn = mod_add_witness(x, y, q, d)
            assert len(asgn) == btn.n_edges
            assert btn.accepts(asgn), f"Valid witness rejected for q={q}, x={x}, y={y}"

            # Corrupt the sum bit
            bad = list(asgn)
            bad[2 * d] = not bad[2 * d]
            assert not btn.accepts(tuple(bad)), f"Corrupted sum accepted for q={q}, x={x}, y={y}"


@pytest.mark.parametrize("q", [2, 3])
def test_mod_mult_table_exhaustive_parsimony(q: int) -> None:
    """Verify table-based modular multiplication parsimony for small moduli."""
    d = q.bit_length()
    btn = mod_mult_table_btn(q, d)

    for x in range(1 << d):
        for y in range(1 << d):
            for z in range(1 << d):
                fixed = {
                    i: bit
                    for i, bit in enumerate(
                        int_to_bits(x, d) + int_to_bits(y, d) + int_to_bits(z, d)
                    )
                }
                observed = btn.count_extensions(fixed)
                expected = 1 if (x < q and y < q and z < q and (x * y) % q == z) else 0
                assert observed == expected, (
                    f"mod_mult_table mismatch for q={q} at ({x}, {y}, {z}): got {observed}, expected {expected}"
                )


@pytest.mark.parametrize("q", [3, 5, 7, 11, 13])
def test_mod_mult_lowdegree_acceptance(q: int) -> None:
    """Verify that mod_mult_lowdegree_btn accepts valid modular products."""
    d = q.bit_length()
    btn = mod_mult_lowdegree_btn(q, d)

    for x in range(q):
        for y in range(q):
            asgn = mod_mult_lowdegree_witness(x, y, q, d)
            assert len(asgn) == btn.n_edges
            assert btn.accepts(asgn), (
                f"Valid modular product rejected for q={q}, x={x}, y={y}, z={(x*y)%q}"
            )

            # Corrupted output residue z must be rejected
            bad = list(asgn)
            bad[2 * d] = not bad[2 * d]
            assert not btn.accepts(tuple(bad)), f"Corrupted residue accepted for q={q}, x={x}, y={y}"


def test_mod_mult_degree_bound() -> None:
    """Verify that Lemma 8 degree is strictly bounded by O(d^{3/4})."""
    for q in [7, 17, 31, 127, 257]:
        d = q.bit_length()
        btn = mod_mult_lowdegree_btn(q, d)

        max_deg = max(len(v.edges) for v in btn.vertices)
        # Theorem 3 degree bound is 136 * (d + 1)^{0.75}
        theoretical_bound = 136 * ((d + 1) ** 0.75)

        assert max_deg <= theoretical_bound, (
            f"Degree bound violated for q={q}, d={d}: {max_deg} > {theoretical_bound}"
        )


def test_mod_word_helper() -> None:
    """Verify mod_word little-endian encoding."""
    word = mod_word(3, 5, 1, 4)
    assert len(word) == 12
    assert bits_to_int(word[:4]) == 3
    assert bits_to_int(word[4:8]) == 5
    assert bits_to_int(word[8:]) == 1
