import pytest

from src.btn.encodings.integer_mult import (
    int_to_bits,
    mult_table_btn,
    mult_word,
    product_language,
)


@pytest.mark.parametrize("d", [1, 2, 3])
def test_table_encoding_is_exact_for_all_words(d):
    btn = mult_table_btn(d)
    for a in range(1 << d):
        for b in range(1 << d):
            for z in range(1 << (2 * d)):
                word = mult_word(a, b, d, z)
                fixed = {edge: bit for edge, bit in enumerate(word)}
                observed = btn.count_extensions(fixed)
                expected = 1 if z == a * b else 0
                assert observed == expected, (d, a, b, z, observed, expected)


@pytest.mark.parametrize("d", [4, 5])
def test_table_encoding_accepts_product_and_rejects_neighbour(d):
    btn = mult_table_btn(d)
    modulus = 1 << (2 * d)
    for a in range(1 << d):
        for b in range(1 << d):
            for z, expected in ((a * b, 1), ((a * b + 1) % modulus, 0)):
                word = mult_word(a, b, d, z)
                observed = btn.count_extensions({edge: bit for edge, bit in enumerate(word)})
                assert observed == expected, (d, a, b, z, observed, expected)


def test_table_encoding_shape():
    for d in range(1, 8):
        btn = mult_table_btn(d)
        assert btn.n_edges == 4 * d
        assert max(len(vertex.edges) for vertex in btn.vertices) == 2 * d + 1
        assert len(btn.vertices) == 2 * d


def test_product_language_size():
    for d in range(1, 5):
        assert len(product_language(d)) == (1 << d) ** 2


def test_int_to_bits_round_trip():
    for width in range(1, 8):
        for value in range(1 << width):
            bits = int_to_bits(value, width)
            assert sum((1 << index) for index, bit in enumerate(bits) if bit) == value
