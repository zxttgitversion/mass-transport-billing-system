import csv

import pytest

from transit_billing import BillingSystem, Constants


def test_billing_system_load_and_generate(tmp_zone_map_file, tmp_journey_file):
    bs = BillingSystem(tmp_zone_map_file, tmp_journey_file)

    bs.load_zone_map()
    assert bs.station_zone_map == {"A": 1, "B": 2, "C": 3}

    bs.load_journey_events()
    assert set(bs.users.keys()) == {"userX", "userY"}
    assert len(bs.users["userX"].events) == 2

    bills = bs.generate_bills(
        Constants.BASE_FEE,
        Constants.PENALTY_FEE,
        Constants.DAY_CAP,
        Constants.MONTH_CAP,
    )

    assert bills == {"userX": pytest.approx(3.30), "userY": pytest.approx(5.00)}


def test_billing_system_write(tmp_path):
    bills = {"uA": 3.3, "uB": 5.0}
    out = tmp_path / "out.csv"

    BillingSystem.write_bills_to_csv(bills, str(out))

    with open(out, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    mapping = {r["user_id"]: float(r["total_bill"]) for r in rows}
    assert mapping == {"uA": pytest.approx(3.30), "uB": pytest.approx(5.00)}
