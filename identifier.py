from __future__ import annotations

from enum import Enum


class Id:

    def __init__(self, val: int, num_bytes: int = 2):
        self.num_bytes = num_bytes
        if val <= 0:
            raise ValueError("Not a positive integer value")
        if val >= (256 ** self.num_bytes):
            raise ValueError("Exceeds max value")
        self.val = val

    def to_bytes(self) -> bytes:
        return self.val.to_bytes(length=self.num_bytes)

    def to_hex(self) -> str:
        return self.to_bytes().hex()

    def __repr__(self) -> str:
        return self.__class__.__name__ + str(self)

    def __str__(self) -> str:
        return str(self.val)


class SubId(Id):

    def __repr__(self) -> str:
        return self.__class__.__name__ + str(self)

    def __str__(self) -> str:
        return str(tuple(self._list_values()))

    def _list_values(self) -> list[int]:
        if isinstance(self.sup, SubId):
            rv = self.sup._list_values()
            rv.append(self.val)
            return rv
        return [self.sup.val, self.val]

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
        assert val <= self.LEVEL_SIZES[self.level]["max_value"], ValueError("Exceeds max value")
        super().__init__(val, num_bytes=SubId.LEVEL_SIZES[self.level]["num_bytes"])
        SubId._last_id_by_level[self.level] = val

    def to_bytes(self) -> bytes:
        return self.sup.to_bytes() + super().to_bytes()
