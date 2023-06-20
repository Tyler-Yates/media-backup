import json

from mediabackup.backup_util import BackupUtil
from mediabackup.logger_util import LoggerUtil

NEWLINE = "\n"


def main():
    input_paths: list[str] = []
    output_paths: list[str] = []

    with open("config.json", mode="r") as config_file:
        config = json.load(config_file)

        input_paths.extend(config["input_paths"])
        output_paths.extend(config["output_paths"])

    print(f"Backing up the following paths:\n{NEWLINE.join(input_paths)}\n")
    print(f"Backing up to the following paths:\n{NEWLINE.join(output_paths)}\n")

    logger_util = LoggerUtil()
    with logger_util:
        backup_util = BackupUtil(input_paths=input_paths, output_paths=output_paths, logger_util=logger_util)
        backup_util.perform_backup()


if __name__ == '__main__':
    main()
    