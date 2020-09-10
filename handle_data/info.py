import json
from json import JSONEncoder
from typing import Any


class Info:
    def __init__(self) -> None:
        self.day = 0
        self.min = 100000.0
        self.max = 100000.0
        self.average = 100000.0

    @staticmethod
    def from_dict(data: dict):
        info = Info()
        info.day = data["day"]
        info.min = data["min"]
        info.max = data["max"]
        info.average = data["average"]
        return info

    def __str__(self) -> str:
        return "{}: {}, {}, {}".format(self.day, self.min, self.max, self.average)


class InfoJSONEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, Info):
            return o.__dict__
        else:
            return json.JSONEncoder.default(self, o)
