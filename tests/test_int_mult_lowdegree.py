"""Tests verifying Theorem 3 low-degree integer multiplication network (Task T06)."""

from __future__ import annotations

import pytest
from src.btn.encodings.integer_mult import mult_word, product_language
from src.btn.encodings.integer_mult_lowdegree import (
    mult_lowdegree_btn,
    mult_lowdegree_params,
    mult_lowdegree_witness,
)


@pytest.mark.parametrize("d", [1, 2, 3])
def test_lowdegree_exhaustive_acceptance(d: int) -> None:
    """Verify that the low-degree BTN accepts all valid products and rejects invalid products."""
    btn = mult_lowdegree_btn(d)

    for a in range(1 << d):
        for b in range(1 << d):
            asgn = mult_lowdegree_witness(a, b, d)
            assert len(asgn) == btn.n_edges
            assert btn.accepts(asgn), f"Failed on valid product {a}*{b}={a*b} for d={d}"

            # Invalid product test: flip the lowest bit of the product
            bad_asgn = list(asgn)
            bad_asgn[2 * d] = not bad_asgn[2 * d]
            assert not btn.accepts(tuple(bad_asgn)), f"Failed to reject invalid product for d={d}, a={a}, b={b}"


def test_edge_and_degree_bounds() -> None:
    """Symbolically verify Theorem 3 edge (< 1100(d+1)) and degree (< 136(d+1)^{3/4}) bounds."""
    for d in range(1, 1025):
        params = mult_lowdegree_params(d)
        J, k, n, L, L1, L2 = (
            params["J"],
            params["k"],
            params["n"],
            params["L"],
            params["L1"],
            params["L2"],
        )
        word_bits = J + 1

        # Total edges bound from Theorem 3
        edge_bound = 1100 * (d + 1)
        # Degree bound from Theorem 3
        degree_bound = 136 * ((d + 1) ** 0.75)

        # Theoretical upper bounds from Lemma 7
        actual_edges_upper = 4 * d + 8 * L * word_bits
        actual_deg_upper = 2 * max(L1, L2) * word_bits

        assert actual_edges_upper < edge_bound, f"Edge bound violated for d={d}: {actual_edges_upper} >= {edge_bound}"
        assert actual_deg_upper < degree_bound, f"Degree bound violated for d={d}: {actual_deg_upper} >= {degree_bound}"


def test_sublinear_degree_scaling() -> None:
    """Verify that degree ratio deg / (d+1) strictly decreases toward 0 as d increases (sub-linear)."""
    ratios = []
    for d in [16, 64, 256, 1024, 4096]:
        params = mult_lowdegree_params(d)
        deg = 2 * max(params["L1"], params["L2"]) * (params["J"] + 1)
        ratio = deg / (d + 1)
        ratios.append(ratio)

    # In a sublinear O(d^{3/4}) function, deg / d -> 0 as d -> inf
    assert ratios[-1] < ratios[0] / 2.0, f"Degree scaling must be strictly sublinear: {ratios}"
