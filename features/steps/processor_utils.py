import time
from typing import Any


def _get_dot_path_json_data(input_data: dict, dot_path: str) -> Any:
    "traverses down the JSON looking for the given path, returns data at that point or raises exception"
    split_path = dot_path.split(".")
    resp_level = input_data
    count = 1

    try:
        for s_level in split_path:
            if isinstance(resp_level, list) or isinstance(resp_level, tuple):
                resp_level = resp_level[int(s_level)]
            else:
                resp_level = resp_level[s_level]

            if count == len(split_path):
                return resp_level
            else:
                count = count + 1
    except KeyError as ex:
        raise ValueError(f"Required Key {str(ex)} Not Found In Response: {dot_path}")
    except IndexError as ex:
        raise ValueError(f"Required Index Not Found In Response: {dot_path}")


def get_dot_path_data(input_data: dict, dot_path: str, data_type: str) -> Any:
    "traverses down the data_type looking for the given path, returns data at that point or raises exception"
    if data_type.lower() == "json":
        return _get_dot_path_json_data(input_data, dot_path)

    raise TypeError(f"Data Type {data_type} Not Supported")


def get_current_time_ms() -> int:
    return int(time.time()) * 1000
