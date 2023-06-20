import json
from typing import Optional

import requests as requests

from mediabackup.backup_util import BackupUtil
from mediabackup.logger_util import LoggerUtil
from mediabackup.recency_util import RecencyUtil

NEWLINE = "\n"


def main():
    input_paths: list[str] = []
    output_paths: list[str] = []
    healthcheck_url: Optional[str] = None

    with open("config.json", mode="r") as config_file:
        config = json.load(config_file)

        input_paths.extend(config["input_paths"])
        output_paths.extend(config["output_paths"])
        healthcheck_url = config["healthcheck_url"]

    print(f"Backing up the following paths:\n{NEWLINE.join(input_paths)}\n")
    print(f"Backing up to the following paths:\n{NEWLINE.join(output_paths)}\n")

    logger_util = LoggerUtil()
    recency_util = RecencyUtil()
    with logger_util:
        backup_util = BackupUtil(input_paths=input_paths, output_paths=output_paths, logger_util=logger_util,
                                 recency_util=recency_util)
        backup_util.perform_backup()

    recency_util.clean_records()

    if healthcheck_url:
        print(f"Pinging healthcheck URL {healthcheck_url}")
        requests.get(healthcheck_url)


if __name__ == '__main__':
    main()
    