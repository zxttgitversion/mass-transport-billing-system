import csv
from datetime import datetime

from transit_billing.models import JourneyEvent, User


def parse_time(time_str):
    """Tokenise time data like '2022-04-04T9:40:00' and convert to datetime."""
    try:
        date_part, time_part = time_str.strip().split("T")
        year, month, day = map(int, date_part.split("-"))
        hour, minute, second = map(int, time_part.split(":"))
        return datetime(year, month, day, hour, minute, second)
    except Exception as e:
        raise ValueError(f"[ERROR] Invalid time format: '{time_str}'. {e}")


def load_zone_map_file(zone_map_file):
    station_zone_map = {}
    required_fields = {"station", "zone"}

    with open(zone_map_file, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        missing = required_fields - set(reader.fieldnames)
        if missing:
            raise KeyError(
                f"[ERROR] zone_map file missing required columns: {missing}. "
                f"Header found: {reader.fieldnames}"
            )

        for row in reader:
            try:
                station_zone_map[row["station"]] = int(row["zone"])
            except KeyError as e:
                raise KeyError(f"[ERROR] zone_map row missing field: {e} in row: {row}")
            except Exception:
                raise ValueError(f"[ERROR] Invalid zone value in row: {row}")

    return station_zone_map


def load_journey_events_file(journey_file):
    users = {}
    required_fields = {"user_id", "station", "direction", "time"}

    with open(journey_file, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        missing = required_fields - set(reader.fieldnames)
        if missing:
            raise KeyError(
                f"[ERROR] journey_data file missing required columns: {missing}. "
                f"Header found: {reader.fieldnames}"
            )

        for row in reader:
            try:
                user_id = row["user_id"]
                event = JourneyEvent(
                    station=row["station"],
                    direction=row["direction"],
                    time=parse_time(row["time"]),
                )
            except KeyError as e:
                raise KeyError(f"[ERROR] journey_data row missing required column: {e} in row: {row}")
            except Exception as e:
                raise ValueError(f"[ERROR] Invalid value in journey_data row: {row}, {e}")

            if user_id not in users:
                users[user_id] = User(user_id)
            users[user_id].add_event(event)

    return users
