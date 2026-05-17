import sys
import csv
from datetime import datetime
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from transit_billing import JourneyEvent


@pytest.fixture
def simple_zone_map():
    return {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6}


def mk_event(station, direction, time_str):
    return JourneyEvent(station, direction, datetime.fromisoformat(time_str))


@pytest.fixture
def tmp_zone_map_file(tmp_path):
    path = tmp_path / "zone_map.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["station", "zone"])
        writer.writerows([["A", "1"], ["B", "2"], ["C", "3"]])
    return str(path)


@pytest.fixture
def tmp_journey_file(tmp_path):
    path = tmp_path / "journey_data.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["user_id", "station", "direction", "time"])
        writer.writerows(
            [
                ["userX", "A", "IN", "2025-06-22T17:30:00"],
                ["userX", "B", "OUT", "2025-06-22T17:40:00"],
                ["userY", "A", "OUT", "2025-06-22T17:40:00"],
            ]
        )
    return str(path)
