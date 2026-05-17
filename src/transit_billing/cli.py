import sys

from transit_billing.billing_service import BillingSystem
from transit_billing.exceptions import BillingError, UnknownStationError
from transit_billing.fare_rules import Constants
from transit_billing.models import JourneyEvent, User


def main():
    if len(sys.argv) != 4:
        raise ValueError(f"Usage: python {sys.argv[0]} <zone_map.csv> <journey_data.csv> <output.csv>")

    zone_map_file = sys.argv[1]
    journey_file = sys.argv[2]
    output_file = sys.argv[3]

    system = BillingSystem(zone_map_file, journey_file)
    system.load_zone_map()
    system.load_journey_events()
    bills = system.generate_bills(
        Constants.BASE_FEE,
        Constants.PENALTY_FEE,
        Constants.DAY_CAP,
        Constants.MONTH_CAP,
    )
    BillingSystem.write_bills_to_csv(bills, output_file)
    print(f"[INFO] Billing results written to {output_file}")


if __name__ == "__main__":
    main()
