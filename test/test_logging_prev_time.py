import os
import pytest
from datetime import datetime
from ..logging_prev_time import (
    get_previous_time_value,
    update_previous_time_value,
    _init_prev_time_data,
)


@pytest.fixture
def get_path() -> str:
    return os.path.join("tmp", "non-existence.txt")


def test_get_previous_time_value_without_file(get_path):
    assert get_previous_time_value(get_path) == _init_prev_time_data()


def test_update_previous_time_value():
    update_previous_time_value("FFA", datetime(2023, 9, 5, 0, 0, 0))
    prev_time_data = get_previous_time_value()
    assert prev_time_data["FFA"] == datetime(2023, 9, 5, 0, 0, 0).isoformat()
