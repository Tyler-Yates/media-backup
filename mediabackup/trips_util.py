from datetime import datetime
from typing import Optional

from mediabackup.trip import Trip


class TripsUtil:
    def __init__(self, trips_config: dict[str, dict[str, str]]):
        self.trips = self.parse_trips_config(trips_config)

    @staticmethod
    def parse_trips_config(trips_config: dict[str, dict[str, str]]) -> list[Trip]:
        trips = []

        for trip_name, config in trips_config.items():
            start_date = datetime.strptime(config["start_date"], '%Y-%m-%d')

            end_date = datetime.strptime(config["end_date"], '%Y-%m-%d')
            # Set end_date to the last possible instant of that day
            end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)

            trip = Trip(name=trip_name, start_date=start_date, end_date=end_date)
            trips.append(trip)

        return trips

    def get_trip_subfolder(self, file_date: datetime) -> Optional[str]:
        for trip in self.trips:
            if trip.is_within_trip(file_date):
                return trip.name

        return None
