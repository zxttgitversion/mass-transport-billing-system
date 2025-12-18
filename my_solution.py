import csv, sys
from datetime import datetime
from collections import defaultdict, deque

class Constants:
    """manages constants centrally"""
    BASE_FEE = 2.00
    PENALTY_FEE = 5.00
    DAY_CAP = 15.00
    MONTH_CAP = 100.00


class JourneyEvent:
    """
    represents ONE tapping event
    """
    def __init__(self, station, direction, time):
        direction = direction.upper()
        if direction not in {'IN', 'OUT'}:
            raise ValueError(f"[ERROR] Invalid direction value: {direction}")
        
        self.station = station
        self.direction = direction
        self.time = time
    
    def __repr__(self):
        return f"JourneyEvent({self.station}, {self.direction}, {self.time})"


class User:
    """
    responsible for 1 aggregating all JourneyEvents for this user
                    2 calculating a bill for this user 
    """
    def __init__(self, user_id):
        self.user_id = user_id
        self.events = []   # List[JourneyEvent]

    def add_event(self, event):
        """adds a JourneyEvent to this user's event list"""
        self.events.append(event)


    def calculate_user_bill(self, station_zone_map, base_fee, penalty_fee, day_cap, month_cap):
        """calculate total bill for this user, with daily and monthly caps."""

        # 1. sort all events for this user in ascending chronological order
        events_sorted = sorted(self.events, key=lambda x: x.time)

        # 2. use 2 dicts to store the daily and monthly cost 
        daily_bill = defaultdict(float)       # dict: daily_bill {day_key (str) -> total_cost (float)}
        monthly_bill = defaultdict(float)     # dict: monthly_bill {month_key (str) -> total_cost (float)}
        
        # 3. use queue to pair IN and OUT
        queue = deque()
        for event in events_sorted:
            if event.direction == 'IN':
                queue.append(event)
            elif event.direction == 'OUT':
                if queue:
                    in_event = queue.popleft()                   # take the earliest unpaired IN from the queue
                    zone_in = station_zone_map[in_event.station]
                    zone_out = station_zone_map[event.station]   # and pair it with the current OUT

                    cost = base_fee + User.zone_cost(zone_in) + User.zone_cost(zone_out)
                    day_key = in_event.time.date().isoformat()   # record "YYYY-MM-DD" 
                    daily_bill[day_key] += cost
                else:
                    cost = penalty_fee   # no IN to pair -> OUT without IN -> penalty
                    day_key = event.time.date().isoformat()  
                    daily_bill[day_key] += cost       

        # if there are still some INs left in the queue
        while queue:
            in_event = queue.popleft()   # no OUT to pair -> IN without OUT -> penalty
            cost = penalty_fee
            day_key = in_event.time.date().isoformat()
            daily_bill[day_key] += cost

        # 4. day capping    
        for day_key in daily_bill:
            if daily_bill[day_key] > day_cap:
                daily_bill[day_key] = day_cap

        # 5. compute monthly_bill 
        for day_key, value in daily_bill.items():
            month_key = day_key[:7]    # use the first 8th char as month_key
            monthly_bill[month_key] += value

        # 6. month capping    
        for month_key in monthly_bill:
            if monthly_bill[month_key] > month_cap:
                monthly_bill[month_key] = month_cap

        # 7. compute total_bill
        total_bill = sum(monthly_bill.values())
        return round(total_bill, 2)  # retained in two decimal places
    
    @staticmethod
    def zone_cost(zone):
        if not isinstance(zone, int):
            raise TypeError(f"[ERROR] zone must be int, got {zone}")
        if zone == 1:
            return 0.80
        elif 2 <= zone <= 3:
            return 0.50
        elif 4 <= zone <= 5:
            return 0.30
        elif zone > 0:
            return 0.10
        else:
            raise ValueError(f"[ERROR] Invalid zone value: {zone}")   
    

class BillingSystem:
    """
    responsible for 1. loading, parsing files
                    2. assembling user objects 
                    3. and invoking calculation logic
    """
    def __init__(self, zone_map_file, journey_file):
        self.zone_map_file = zone_map_file
        self.journey_file = journey_file
        self.station_zone_map = {}  # dict: station_zone_map {station (str) -> zone (int)}
        self.users = {}             # dict: users {user_id (str) -> User}

    @staticmethod
    def my_parse_time_function(time_str):
        """ tokenise time data like '2022-04-04T9:40:00' and convert to datetime """
        try:
            date_part, time_part = time_str.strip().split('T')
            year, month, day = map(int, date_part.split('-'))
            hour, minute, second = map(int, time_part.split(':'))
            return datetime(year, month, day, hour, minute, second)
        except Exception as e:
            raise ValueError(f"[ERROR] Invalid time format: '{time_str}'. {e}")

    def load_zone_map(self):
        required_fields = {'station', 'zone'}
        with open(self.zone_map_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            missing = required_fields - set(reader.fieldnames)
            if missing:
                raise KeyError(f"[ERROR] zone_map file missing required columns: {missing}. "
                               f"Header found: {reader.fieldnames}")
            
            for row in reader:
                try:
                    self.station_zone_map[row['station']] = int(row['zone'])
                except KeyError as e:
                    raise KeyError(f"[ERROR] zone_map row missing field: {e} in row: {row}")
                except Exception:
                    raise ValueError(f"[ERROR] Invalid zone value in row: {row}")

    def load_journey_events(self):
        """ load all JourneyEvent objects for each user from csv """

        required_fields = {'user_id', 'station', 'direction', 'time'}
        with open(self.journey_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            missing = required_fields - set(reader.fieldnames)
            if missing:
                raise KeyError(f"[ERROR] journey_data file missing required columns: {missing}. "
                               f"Header found: {reader.fieldnames}")
            
            for row in reader:
                try:
                    user_id = row['user_id']
                    event = JourneyEvent(
                        station=row['station'],
                        direction=row['direction'],
                        time=BillingSystem.my_parse_time_function(row['time'])
                    )
                except KeyError as e:
                    raise KeyError(f"[ERROR] journey_data row missing required column: {e} in row: {row}")
                except Exception as e:
                    raise ValueError(f"[ERROR] Invalid value in journey_data row: {row}, {e}")
                
                if user_id not in self.users:
                    self.users[user_id] = User(user_id)
                self.users[user_id].add_event(event)

    def generate_bills(self, base_fee, penalty_fee, day_cap, month_cap):
        """ call calculate_user_bill() for each user """

        bills = {}       # dict: bills { user_id (str) -> total_bill (float) }
        for user_id, user in self.users.items():
            bills[user_id] = user.calculate_user_bill(
                self.station_zone_map, base_fee, penalty_fee, day_cap, month_cap
            )
        return bills

    @staticmethod
    def write_bills_to_csv(bills_dict, filename):
        with open(filename, "w", newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["user_id", "total_bill"])
            for user_id, bill in bills_dict.items():
                writer.writerow([user_id, bill])


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
        Constants.MONTH_CAP
    )
    BillingSystem.write_bills_to_csv(bills, output_file)
    print(f"[INFO] Billing results written to {output_file}")

if __name__ == "__main__":
    main()
