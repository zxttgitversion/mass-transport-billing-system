import csv

from transit_billing.parser import load_journey_events_file, load_zone_map_file, parse_time


class BillingSystem:
    """
    Loads input files, assembles user objects, and invokes billing calculation.
    """

    def __init__(self, zone_map_file, journey_file):
        self.zone_map_file = zone_map_file
        self.journey_file = journey_file
        self.station_zone_map = {}
        self.users = {}

    @staticmethod
    def my_parse_time_function(time_str):
        return parse_time(time_str)

    def load_zone_map(self):
        self.station_zone_map = load_zone_map_file(self.zone_map_file)

    def load_journey_events(self):
        self.users = load_journey_events_file(self.journey_file)

    def generate_bills(self, base_fee, penalty_fee, day_cap, month_cap):
        """Call calculate_user_bill() for each user."""
        bills = {}
        for user_id, user in self.users.items():
            bills[user_id] = user.calculate_user_bill(
                self.station_zone_map, base_fee, penalty_fee, day_cap, month_cap
            )
        return bills

    @staticmethod
    def write_bills_to_csv(bills_dict, filename):
        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["user_id", "total_bill"])
            for user_id, bill in bills_dict.items():
                writer.writerow([user_id, bill])
