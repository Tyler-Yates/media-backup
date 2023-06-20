import os
import pathlib
import shutil
import sys
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
        self.output_path_to_file_name_to_existing_file_data: dict[str, dict[str, list[FileData]]] = defaultdict(
            lambda: defaultdict(list))

        self.copies = []
        self.skips = []
        self.errors = []

    def _collect_file(self, absolute_path: str):
        if file_util.should_ignore_file(absolute_path):
            print(f"Ignoring {absolute_path}")
            return

        print(f"Found {absolute_path}")
        year_taken = file_util.get_file_year(absolute_path)
        self.year_to_paths_to_backup[year_taken].append(FileData(absolute_path))

    def _collect_existing_files_for_templated_path(self, templated_path: str):
        for root, dirs, files in os.walk(templated_path):
            for filename in files:
                absolute_path = os.path.join(root, filename)
                self.output_path_to_file_name_to_existing_file_data[templated_path][filename]\
                    .append(FileData(absolute_path))

    def _collect_existing_files(self):
        for year in self.year_to_paths_to_backup.keys():
            templated_paths = [self._get_photo_path(output_path, year) for output_path in self.output_paths]
            templated_paths.extend([self._get_video_path(output_path, year) for output_path in self.output_paths])
            for templated_path in templated_paths:
                self._collect_existing_files_for_templated_path(templated_path)

    def _backup_file_to_path(self, output_path: str, year: int, file_to_backup: FileData):
        # Make sure we have not already copied the file
        existing_files = self.output_path_to_file_name_to_existing_file_data[output_path] \
            .get(file_to_backup.file_name, [])
        for existing_file in existing_files:
            if existing_file.size == file_to_backup.size and existing_file.checksum == file_to_backup.checksum:
                self.logger_util.write(f"File {existing_file.absolute_path} already exists"
                                       f" so skipping backup of {file_to_backup.absolute_path}")
                self.skips.append(file_to_backup.absolute_path)
                return
            else:
                print(f"File {existing_file.absolute_path} already exists but appears to be a different file.")

        # If we have gotten to this point, we need to copy the file.
        self.logger_util.write(f"Copying file {file_to_backup.absolute_path} to {output_path}")
        pathlib.Path(output_path).mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_to_backup.absolute_path, output_path)
        self.copies.append(file_to_backup.absolute_path)

        # Make sure the copy was successful
        copied_file = FileData(os.path.join(output_path, file_to_backup.file_name))
        if file_to_backup.size != copied_file.size or file_to_backup.checksum != copied_file.checksum:
            self.logger_util.write(f"ERROR! Copied file {copied_file.absolute_path} is not"
                                   f" equal to original file {file_to_backup.absolute_path}")
            self.errors.append(file_to_backup.absolute_path)

    def _backup_file(self, year: int, file_to_backup: FileData):
        for output_path in self._get_output_paths_for_file(year, file_to_backup):
            self._backup_file_to_path(output_path, year, file_to_backup)

    def _backup_path(self, input_path: str):
        self.logger_util.write(f"Processing input path {input_path}...")
        for root, dirs, files in os.walk(input_path):
            for filename in files:
                absolute_path = os.path.join(root, filename)
                self._collect_file(absolute_path)

        self._collect_existing_files()

        for year, files_to_backup in self.year_to_paths_to_backup.items():
            for file_to_backup in files_to_backup:
                self._backup_file(year, file_to_backup)

    @staticmethod
    def _get_photo_path(output_path: str, year: int):
        return os.path.join(output_path, "Photos", str(year))

    @staticmethod
    def _get_video_path(output_path: str, year: int):
        return os.path.join(output_path, "Videos", str(year))

    def _get_output_paths_for_file(self, year: int, file_data: FileData) -> list[str]:
        if file_data.is_image:
            return [self._get_photo_path(output_path, year) for output_path in self.output_paths]
        elif file_data.is_video:
            return [self._get_video_path(output_path, year) for output_path in self.output_paths]

    def perform_backup(self):
        self.year_to_paths_to_backup.clear()
        self.output_path_to_file_name_to_existing_file_data.clear()
        self.copies.clear()
        self.skips.clear()
        self.errors.clear()

        for input_path in self.input_paths:
            self._backup_path(input_path)

        self.logger_util.write(f"\nCopies: {len(self.copies)}")
        self.logger_util.write(f"Skips: {len(self.skips)}")
        self.logger_util.write(f"Errors: {len(self.errors)}")

        if len(self.errors) > 0:
            sys.exit(1)
