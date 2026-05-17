from collections import defaultdict, deque

from transit_billing.exceptions import UnknownStationError
from transit_billing.fare_rules import zone_cost


class JourneyEvent:
    """Represents one tapping event."""

    def __init__(self, station, direction, time):
        direction = direction.upper()
        if direction not in {"IN", "OUT"}:
            raise ValueError(f"[ERROR] Invalid direction value: {direction}")

        self.station = station
        self.direction = direction
        self.time = time

    def __repr__(self):
        return f"JourneyEvent({self.station}, {self.direction}, {self.time})"


class User:
    """Aggregates journey events and calculates a bill for one user."""

    def __init__(self, user_id):
        self.user_id = user_id
        self.events = []

    def add_event(self, event):
        """Add a JourneyEvent to this user's event list."""
        self.events.append(event)

    def calculate_user_bill(self, station_zone_map, base_fee, penalty_fee, day_cap, month_cap):
        """Calculate total bill for this user, with daily and monthly caps."""
        events_sorted = sorted(self.events, key=lambda x: x.time)

        daily_bill = defaultdict(float)
        monthly_bill = defaultdict(float)

        queue = deque()
        for event in events_sorted:
            if event.direction == "IN":
                queue.append(event)
            elif event.direction == "OUT":
                if queue:
                    in_event = queue.popleft()
                    zone_in = self._lookup_station_zone(station_zone_map, in_event.station)
                    zone_out = self._lookup_station_zone(station_zone_map, event.station)

                    cost = base_fee + User.zone_cost(zone_in) + User.zone_cost(zone_out)
                    day_key = in_event.time.date().isoformat()
                    daily_bill[day_key] += cost
                else:
                    cost = penalty_fee
                    day_key = event.time.date().isoformat()
                    daily_bill[day_key] += cost

        while queue:
            in_event = queue.popleft()
            cost = penalty_fee
            day_key = in_event.time.date().isoformat()
            daily_bill[day_key] += cost

        for day_key in daily_bill:
            if daily_bill[day_key] > day_cap:
                daily_bill[day_key] = day_cap

        for day_key, value in daily_bill.items():
            month_key = day_key[:7]
            monthly_bill[month_key] += value

        for month_key in monthly_bill:
            if monthly_bill[month_key] > month_cap:
                monthly_bill[month_key] = month_cap

        total_bill = sum(monthly_bill.values())
        return round(total_bill, 2)

    @staticmethod
    def zone_cost(zone):
        return zone_cost(zone)

    @staticmethod
    def _lookup_station_zone(station_zone_map, station):
        try:
            return station_zone_map[station]
        except KeyError:
            raise UnknownStationError(f"[ERROR] Unknown station in journey data: {station}")
