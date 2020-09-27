import time
from typing import Any


def get_dot_path_data(input_data, dot_path, data_type) -> Any:
    "traverses down the JSON looking for the given path, returns data at that point, None if error or raises exception"
    if data_type.lower() == "json":
        # find json dotpath and return data
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
        except Exception:
            raise Exception("Required Key Not Found In Response: " + dot_path)
    if data_type.lower() == "xml":
        # find xml path and return data
        xml_path = dot_path.replace(".", "/")
        xml_node = input_data.find(xml_path)

        if xml_node is not None:
            return xml_node.text.replace("\n", "")
        raise Exception("Required Path not Found In Response: " + dot_path)

    raise Exception("Data Type " + data_type + " Not Supported")


def get_current_time_ms():
    return time.time() * 1000
