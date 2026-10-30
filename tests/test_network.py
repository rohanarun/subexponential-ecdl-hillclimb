import pytest

from src.btn.encodings.lookup import lookup_btn
from src.btn.network import BTN, Vertex, check_parsimony


def test_and_network_contracts_to_one_assignment():
    btn = BTN(n_edges=2, vertices=(Vertex((0, 1), lambda bits: bits[0] and bits[1]),))
    assert btn.contract() == 1
    assert list(btn.satisfying_assignments()) == [(True, True)]


def test_count_extensions_only_enumerates_free_edges():
    btn = BTN(n_edges=2, vertices=(Vertex((0, 1), lambda bits: bits[0] and bits[1]),))
    assert btn.count_extensions({0: True}) == 1
    assert btn.count_extensions({0: False}) == 0
    assert btn.count_extensions({0: True, 1: True}) == 1
    assert btn.count_extensions({0: True, 1: False}) == 0


def test_invalid_edge_is_rejected():
    with pytest.raises(ValueError):
        BTN(n_edges=1, vertices=(Vertex((2,), lambda bits: True),))
    btn = BTN(n_edges=1, vertices=(Vertex((0,), lambda bits: True),))
    with pytest.raises(ValueError):
        btn.count_extensions({3: True})


def test_lookup_encoding_is_parsimonious_for_xor():
    btn = lookup_btn(2, lambda bits: bits[0] ^ bits[1])
    language = [(False, True), (True, False)]
    assert check_parsimony(btn, language) == []
    assert btn.contract() == 2


def test_check_parsimony_reports_mismatches():
    btn = lookup_btn(2, lambda bits: bits[0] ^ bits[1])
    failures = check_parsimony(btn, [(False, False)])
    assert len(failures) == 3
    assert (False, False) in {word for word, _, _ in failures}


def test_interface_word_matches_assignment():
    btn = BTN(
        n_edges=3,
        vertices=(Vertex((0, 2), lambda bits: bits[0] == bits[1]),),
        interface=(1, 2),
    )
    assert btn.interface_word((False, True, True)) == (True, True)
    assert btn.count_extensions({1: True, 2: True}) == 1
