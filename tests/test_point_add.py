from src.btn.ec.curve import INFINITY, Curve, Point
from src.btn.encodings.point_add import (
    bits_per_coord,
    decode_point,
    encode_point,
    point_add_btn,
    point_word,
)


def test_point_encoding_round_trip():
    curve = Curve(7, 2, 3)
    width = bits_per_coord(curve)
    for point in [INFINITY] + curve.points():
        assert decode_point(encode_point(point, width), width) == point


def test_point_add_lookup_matches_curve_arithmetic():
    curve = Curve(7, 2, 3)
    width = bits_per_coord(curve)
    btn = point_add_btn(curve, width)
    points = [INFINITY] + curve.points()
    for p1 in points:
        for p2 in points:
            expected = curve.add(p1, p2)
            for p3 in points:
                assert btn.accepts(point_word(p1, p2, p3, width)) == (p3 == expected)


def test_noncanonical_infinity_is_rejected():
    curve = Curve(7, 2, 3)
    width = bits_per_coord(curve)
    btn = point_add_btn(curve, width)
    word = list(point_word(INFINITY, INFINITY, INFINITY, width))
    word[1] = True  # infinity flag set, but x != 0
    assert not btn.accepts(tuple(word))


def test_off_curve_point_is_rejected():
    curve = Curve(7, 2, 3)
    width = bits_per_coord(curve)
    btn = point_add_btn(curve, width)
    # (0, 0) is not on y^2 = x^3 + 2x + 3 over F_7.
    assert not curve.on_curve(Point(0, 0))
    word = point_word(Point(0, 0), INFINITY, Point(0, 0), width)
    assert not btn.accepts(word)
