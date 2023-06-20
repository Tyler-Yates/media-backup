import os
import pickle
from datetime import datetime
from typing import Optional, Tuple, Dict

from atomicwrites import atomic_write

from mediabackup.file_data import FileData

RECENCY_FILE_NAME = "recency.pickle"
RECENCY_MINIMUM_AGE_DAYS = 90

# Tuple structure
# (processing date, size, modified time)


class RecencyUtil:
    def __init__(self, recency_file_path=RECENCY_FILE_NAME):
        self.recency_dict: Dict[str, Tuple] = dict()
        self.recency_file_path = recency_file_path

        if os.path.exists(self.recency_file_path):
            with open(self.recency_file_path, mode="rb") as recency_file:
                self.recency_dict = pickle.load(recency_file)

    def _save_pickle(self):
        with atomic_write(self.recency_file_path, mode="wb", overwrite=True) as recency_file:
            recency_file.write(pickle.dumps(self.recency_dict, protocol=pickle.HIGHEST_PROTOCOL))

    def record_file_processed(self, file_data: FileData):
        self.recency_dict[file_data.absolute_path] = (datetime.now(), file_data.size, file_data.modified_time)
        self._save_pickle()

    def file_processed_recently(self, file_data: FileData) -> bool:
        recency_tuple: Optional[Tuple[datetime, datetime]] = self.recency_dict.get(file_data.absolute_path, None)
        if recency_tuple is None:
            return False

        processed_date = recency_tuple[0]
        recorded_file_size = recency_tuple[1]
        recorded_file_modified_time = recency_tuple[2]

        # If the file was modified since the last time we saw it, we need to check it again
        if file_data.size != recorded_file_size:
            self._remove_recency_record(file_data.absolute_path)
            return False
        if file_data.modified_time != recorded_file_modified_time:
            self._remove_recency_record(file_data.absolute_path)
            return False

        # If the file is not modified, check if we should read it fully
        datetime_diff = datetime.now() - processed_date
        return datetime_diff.days < RECENCY_MINIMUM_AGE_DAYS

    def clean_records(self, age_in_days_to_clean=RECENCY_MINIMUM_AGE_DAYS):
        file_paths_to_remove = []

        for file_path, information_tuple in self.recency_dict.items():
            days_since_record = (datetime.now() - information_tuple[0]).days
            if days_since_record >= age_in_days_to_clean:
                file_paths_to_remove.append(file_path)

        for file_path in file_paths_to_remove:
            self.recency_dict.pop(file_path)
        self._save_pickle()

    def _remove_recency_record(self, absolute_file_path: str):
        removed_record = self.recency_dict.pop(absolute_file_path, None)

        if removed_record is None:
            print(f"File path {absolute_file_path} was not in the recency dictionary")
        else:
            self._save_pickle()
