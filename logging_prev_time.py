import json
import os
from datetime import datetime
from settings import get_settings, DevSettings, ProdSettings
from typing import Dict


settings = get_settings()


def get_json_file_path():
    if "PYTEST_CURRENT_TEST" in os.environ:
        # Running as a pytest unit test
        file_path = os.path.join("test", "data", settings.PREV_TIME_FILENAME)
    else:
        # Running in production
        file_path = os.path.join("data", settings.PREV_TIME_FILENAME)
    return file_path


def _init_prev_time_data() -> Dict:
    prev_time_data = {}
    for report_name in settings.FIS_FILENAME_PREFIX.keys():
        prev_time_data[report_name] = datetime(1970, 1, 1, 0, 0, 0).isoformat()
    return prev_time_data


def _read_file() -> Dict:
    with open(get_json_file_path(), "r") as file:
        prev_time_data = json.load(file)
    return prev_time_data


def get_previous_time_value(path=None):
    if path is None:
        path = get_json_file_path()

    if os.path.exists(path):
        prev_time_data = _read_file()
    else:
        prev_time_data = _init_prev_time_data()

    return prev_time_data


def update_previous_time_value(report_name: str, curr_time_value: datetime):
    if os.path.exists(get_json_file_path()):
        prev_time_data = _read_file()
        prev_time_data[report_name] = curr_time_value.isoformat()
    else:
        prev_time_data = _init_prev_time_data()
    with open(get_json_file_path(), "w") as file:
        json.dump(prev_time_data, file, indent=4)
