import pytest

from src.btn.ec.curve import Curve, Point
from src.btn.ecdl import toy_index_calculus


@pytest.fixture(scope="module")
def toy_curve():
    curve = Curve(101, 6, 9)
    generator = Point(0, 3)
    assert curve.is_prime_order()
    assert curve.order() == 83
    assert curve.mul(83, generator).is_infinity
    return curve, generator


@pytest.mark.parametrize("seed,xi", [(0, 19), (1, 75), (2, 3)])
def test_toy_index_calculus_recovers_xi(toy_curve, seed, xi):
    curve, generator = toy_curve
    target = curve.mul(xi, generator)
    result = toy_index_calculus(curve, generator, target, m=2, seed=seed)
    assert result.success, result.reason
    assert result.xi == xi
    assert curve.mul(result.xi, generator) == target


def test_toy_index_calculus_with_three_factor_bases(toy_curve):
    curve, generator = toy_curve
    xi = 42
    target = curve.mul(xi, generator)
    result = toy_index_calculus(curve, generator, target, m=3, seed=7)
    assert result.success, result.reason
    assert result.xi == xi


def test_non_prime_order_curve_is_rejected():
    curve = Curve(7, 2, 3)
    if curve.is_prime_order():
        pytest.skip("the small test curve happens to be prime-order")
    with pytest.raises(ValueError):
        toy_index_calculus(curve, curve.points()[0], curve.points()[1], m=2)
