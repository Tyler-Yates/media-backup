from datetime import datetime


class Trip:
    def __init__(self, name: str, start_date: datetime, end_date: datetime):
        self.name = name
        self.start_date = start_date
        self.end_date = end_date

    def is_within_trip(self, file_date: datetime) -> bool:
        return self.start_date <= file_date <= self.end_date
