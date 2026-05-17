import pytest

from transit_billing import User


def test_zone_cost_valid():
    assert User.zone_cost(1) == pytest.approx(0.80)
    assert User.zone_cost(2) == pytest.approx(0.50)
    assert User.zone_cost(5) == pytest.approx(0.30)
    assert User.zone_cost(999) == pytest.approx(0.10)


def test_zone_cost_errors():
    with pytest.raises(TypeError):
        User.zone_cost("not_int")
    with pytest.raises(ValueError):
        User.zone_cost(0)
    with pytest.raises(ValueError):
        User.zone_cost(-3)
