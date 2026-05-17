import pytest

from transit_billing import Constants, UnknownStationError, User
from tests.conftest import mk_event


def test_calculate_user_bill_round_trip(simple_zone_map):
    user = User("u1")
    user.add_event(mk_event("A", "IN", "2025-06-06T08:00:00"))
    user.add_event(mk_event("B", "OUT", "2025-06-06T08:30:00"))

    total = user.calculate_user_bill(
        station_zone_map=simple_zone_map,
        base_fee=Constants.BASE_FEE,
        penalty_fee=Constants.PENALTY_FEE,
        day_cap=Constants.DAY_CAP,
        month_cap=Constants.MONTH_CAP,
    )

    assert total == pytest.approx(3.30)


def test_calculate_user_bill_penalty(simple_zone_map):
    user = User("u2")
    user.add_event(mk_event("B", "OUT", "2025-06-06T09:00:00"))
    user.add_event(mk_event("C", "IN", "2025-06-06T09:30:00"))

    total = user.calculate_user_bill(
        station_zone_map=simple_zone_map,
        base_fee=Constants.BASE_FEE,
        penalty_fee=Constants.PENALTY_FEE,
        day_cap=Constants.DAY_CAP,
        month_cap=Constants.MONTH_CAP,
    )

    assert total == pytest.approx(10.00)


def test_calculate_user_bill_unknown_station_raises_domain_error(simple_zone_map):
    user = User("u_unknown")
    user.add_event(mk_event("A", "IN", "2025-06-06T08:00:00"))
    user.add_event(mk_event("Z", "OUT", "2025-06-06T08:30:00"))

    with pytest.raises(UnknownStationError, match="Unknown station"):
        user.calculate_user_bill(
            station_zone_map=simple_zone_map,
            base_fee=Constants.BASE_FEE,
            penalty_fee=Constants.PENALTY_FEE,
            day_cap=Constants.DAY_CAP,
            month_cap=Constants.MONTH_CAP,
        )


def test_calculate_user_bill_daily_cap(simple_zone_map):
    user = User("u_daily_cap")
    for hour in range(6):
        user.add_event(mk_event("A", "IN", f"2025-06-06T{hour:02d}:00:00"))
        user.add_event(mk_event("B", "OUT", f"2025-06-06T{hour:02d}:20:00"))

    total = user.calculate_user_bill(
        station_zone_map=simple_zone_map,
        base_fee=Constants.BASE_FEE,
        penalty_fee=Constants.PENALTY_FEE,
        day_cap=Constants.DAY_CAP,
        month_cap=Constants.MONTH_CAP,
    )

    assert total == pytest.approx(Constants.DAY_CAP)


def test_calculate_user_bill_monthly_cap(simple_zone_map):
    user = User("u_monthly_cap")
    for day in range(1, 9):
        for hour in range(5):
            user.add_event(mk_event("A", "IN", f"2025-06-{day:02d}T{hour:02d}:00:00"))
            user.add_event(mk_event("B", "OUT", f"2025-06-{day:02d}T{hour:02d}:20:00"))

    total = user.calculate_user_bill(
        station_zone_map=simple_zone_map,
        base_fee=Constants.BASE_FEE,
        penalty_fee=Constants.PENALTY_FEE,
        day_cap=Constants.DAY_CAP,
        month_cap=Constants.MONTH_CAP,
    )

    assert total == pytest.approx(Constants.MONTH_CAP)


def test_calculate_user_bill_crossing_multiple_zones(simple_zone_map):
    user = User("u_multi_zone")
    user.add_event(mk_event("A", "IN", "2025-06-06T08:00:00"))
    user.add_event(mk_event("F", "OUT", "2025-06-06T08:30:00"))

    total = user.calculate_user_bill(
        station_zone_map=simple_zone_map,
        base_fee=Constants.BASE_FEE,
        penalty_fee=Constants.PENALTY_FEE,
        day_cap=Constants.DAY_CAP,
        month_cap=Constants.MONTH_CAP,
    )

    assert total == pytest.approx(2.90)


def test_calculate_user_bill_repeated_out(simple_zone_map):
    user = User("u_repeated_out")
    user.add_event(mk_event("A", "IN", "2025-06-06T08:00:00"))
    user.add_event(mk_event("B", "OUT", "2025-06-06T08:30:00"))
    user.add_event(mk_event("C", "OUT", "2025-06-06T09:00:00"))

    total = user.calculate_user_bill(
        station_zone_map=simple_zone_map,
        base_fee=Constants.BASE_FEE,
        penalty_fee=Constants.PENALTY_FEE,
        day_cap=Constants.DAY_CAP,
        month_cap=Constants.MONTH_CAP,
    )

    assert total == pytest.approx(8.30)


def test_calculate_user_bill_repeated_in(simple_zone_map):
    user = User("u_repeated_in")
    user.add_event(mk_event("A", "IN", "2025-06-06T08:00:00"))
    user.add_event(mk_event("B", "IN", "2025-06-06T08:10:00"))
    user.add_event(mk_event("C", "OUT", "2025-06-06T08:30:00"))

    total = user.calculate_user_bill(
        station_zone_map=simple_zone_map,
        base_fee=Constants.BASE_FEE,
        penalty_fee=Constants.PENALTY_FEE,
        day_cap=Constants.DAY_CAP,
        month_cap=Constants.MONTH_CAP,
    )

    assert total == pytest.approx(8.30)
