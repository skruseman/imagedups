from __future__ import annotations

from enum import Enum


class Id (object):
    def __init__(self, val: int = 0, num_bytes: int = 2):
        self.val = val
        self.num_bytes = num_bytes
    def to_bytes(self):
        return self.val.to_bytes(length=self.num_bytes)


class SubId(Id):
    class Level(Enum):
        ONE = 1
        TWO = 2

    LEVEL_SIZES = {
        Level.ONE: {"num_bytes": 2, "max_value": 256**2 - 1},
        Level.TWO: {"num_bytes": 4, "max_value": 256**4 - 1},
    }

    _last_id_by_level = {
        Level.ONE: 0,
        Level.TWO: 0,
    }

    def __init__(self, sup: Id):
        self.sup = sup
        if isinstance(sup, SubId):
            assert sup.level == SubId.Level.ONE, "No unexpected nesting level"
            self.level = SubId.Level.TWO
        else:  # sup is of class: Id
            self.level = SubId.Level.ONE

        last_id = SubId._last_id_by_level[self.level]
        val = last_id + 1
        assert val <= self.LEVEL_SIZES[self.level]["MAX_value"], ValueError("Exceeds max value")
        super().__init__(val, num_bytes=SubId.LEVEL_SIZES[self.level]["num_bytes"])
        SubId._last_id_by_level[self.level] = val

    def to_bytes(self):
        return self.sup.to_bytes() + super().to_bytes()
