from datetime import datetime

import pytest

from transit_billing.parser import load_journey_events_file, load_zone_map_file, parse_time


def write_csv(path, header, rows):
    path.write_text(
        "\n".join(
            [
                ",".join(header),
                *[",".join(row) for row in rows],
            ]
        ),
        encoding="utf-8",
    )
    return str(path)


def test_parse_time_valid():
    assert parse_time("2025-06-06T08:30:00") == datetime(2025, 6, 6, 8, 30, 0)


def test_parse_time_accepts_single_digit_hour():
    assert parse_time("2025-06-06T8:30:00") == datetime(2025, 6, 6, 8, 30, 0)


def test_parse_time_invalid_format_raises_value_error():
    with pytest.raises(ValueError, match="Invalid time format"):
        parse_time("2025/06/06 08:30:00")


def test_load_zone_map_file_valid(tmp_path):
    path = write_csv(
        tmp_path / "zone_map.csv",
        ["station", "zone"],
        [["A", "1"], ["B", "2"]],
    )

    assert load_zone_map_file(path) == {"A": 1, "B": 2}


def test_load_zone_map_file_missing_station_column(tmp_path):
    path = write_csv(
        tmp_path / "zone_map.csv",
        ["name", "zone"],
        [["A", "1"]],
    )

    with pytest.raises(KeyError, match="missing required columns"):
        load_zone_map_file(path)


def test_load_zone_map_file_missing_zone_column(tmp_path):
    path = write_csv(
        tmp_path / "zone_map.csv",
        ["station", "area"],
        [["A", "1"]],
    )

    with pytest.raises(KeyError, match="missing required columns"):
        load_zone_map_file(path)


def test_load_zone_map_file_invalid_zone_value(tmp_path):
    path = write_csv(
        tmp_path / "zone_map.csv",
        ["station", "zone"],
        [["A", "not-a-zone"]],
    )

    with pytest.raises(ValueError, match="Invalid zone value"):
        load_zone_map_file(path)


def test_load_journey_events_file_valid(tmp_path):
    path = write_csv(
        tmp_path / "journey_data.csv",
        ["user_id", "station", "direction", "time"],
        [
            ["user1", "A", "IN", "2025-06-06T08:00:00"],
            ["user1", "B", "OUT", "2025-06-06T08:30:00"],
            ["user2", "C", "OUT", "2025-06-06T09:00:00"],
        ],
    )

    users = load_journey_events_file(path)

    assert set(users.keys()) == {"user1", "user2"}
    assert len(users["user1"].events) == 2
    assert users["user1"].events[0].station == "A"
    assert users["user1"].events[0].direction == "IN"
    assert users["user1"].events[0].time == datetime(2025, 6, 6, 8, 0, 0)


@pytest.mark.parametrize(
    "missing_column,header",
    [
        ("user_id", ["station", "direction", "time"]),
        ("station", ["user_id", "direction", "time"]),
        ("direction", ["user_id", "station", "time"]),
        ("time", ["user_id", "station", "direction"]),
    ],
)
def test_load_journey_events_file_missing_required_column(tmp_path, missing_column, header):
    row_by_column = {
        "user_id": "user1",
        "station": "A",
        "direction": "IN",
        "time": "2025-06-06T08:00:00",
    }
    path = write_csv(
        tmp_path / "journey_data.csv",
        header,
        [[row_by_column[column] for column in header]],
    )

    with pytest.raises(KeyError, match="missing required columns"):
        load_journey_events_file(path)


def test_load_journey_events_file_invalid_direction(tmp_path):
    path = write_csv(
        tmp_path / "journey_data.csv",
        ["user_id", "station", "direction", "time"],
        [["user1", "A", "SIDEWAYS", "2025-06-06T08:00:00"]],
    )

    with pytest.raises(ValueError, match="Invalid value in journey_data row"):
        load_journey_events_file(path)


def test_load_journey_events_file_invalid_time(tmp_path):
    path = write_csv(
        tmp_path / "journey_data.csv",
        ["user_id", "station", "direction", "time"],
        [["user1", "A", "IN", "not-a-time"]],
    )

    with pytest.raises(ValueError, match="Invalid value in journey_data row"):
        load_journey_events_file(path)
