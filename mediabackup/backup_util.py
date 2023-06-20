import os
from collections import defaultdict

from mediabackup import file_util
from mediabackup.file_data import FileData
from mediabackup.logger_util import LoggerUtil


class BackupUtil:
    def __init__(self, input_paths: list[str], output_paths: list[str], logger_util: LoggerUtil):
        self.input_paths = input_paths
        self.output_paths = output_paths
        self.logger_util = logger_util

        self.year_to_paths_to_backup: dict[int, list[FileData]] = defaultdict(list)

    def _collect_file(self, absolute_path: str):
        if file_util.should_ignore_file(absolute_path):
            print(f"Ignoring {absolute_path}")
            return

        print(f"Found {absolute_path}")
        year_taken = file_util.get_file_year(absolute_path)
        self.year_to_paths_to_backup[year_taken].append(FileData(absolute_path))

    def _backup_path(self, input_path: str):
        self.logger_util.write(f"Processing input path {input_path}...")
        for root, dirs, files in os.walk(input_path):
            for filename in files:
                absolute_path = os.path.join(root, filename)
                self._collect_file(absolute_path)

    def perform_backup(self):
        self.year_to_paths_to_backup.clear()

        for input_path in self.input_paths:
            self._backup_path(input_path)
