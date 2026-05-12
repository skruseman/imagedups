from __future__ import annotations

from enum import Enum


class Id:
    """Provides identifiers fitting a fixed number of bytes.

    Values are provided by the user and should be positive integers > 1 and
    < 256**N where N is the number of bytes.
    Uniqueness is not supported; if so desired, it is the responsibility of the user.
    Specialized testing for equality of instances is not supported.
    """

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
        return self.__class__.__name__ + f'({self})'

    def __str__(self) -> str:
        return str(self.val)


class CompositeId(Id):
    """Generates identifiers consisting of a sequence of integer values,
    adding a component to the provided base identifier. E.g.:

    Values generated are positive identifiers starting at 1, incrementing with each identifier.

    id_1 = Id(42)             #  42
    id_2 = CompositeId(id_1)  # (42, 1)
    id_3 = CompositeId(id_1)  # (42, 2)
    id_4 = CompositeId(id_3)  # (42, 2, 1)

    Each generated identifier will be unique with respect to its first and most significant value.
    This uniqueness applies only to a single python session.

    Each component value fits a fixed number of bytes N, with the highest value being (256**N - 1).
    The number of bytes is defined in this class, and can differ from level to level.
    For number of bytes for the most significant value see class Id.
    Specialized testing for equality of instances is not supported.
    """

    class Level(Enum):
        ONE = 1
        TWO = 2

    NUM_BYTES = {
        Level.ONE: 2,
        Level.TWO: 4,
    }

    _last_id_by_level = {
        Level.ONE: 0,
        Level.TWO: 0,
    }

    @staticmethod
    def _max_value(level: CompositeId.Level) -> int:
        return 256**CompositeId.NUM_BYTES[level] - 1

    def __init__(self, base: Id):
        self.base = base
        if isinstance(base, CompositeId):
            assert base.level == CompositeId.Level.ONE, "Nesting beyond two sub-levels is not supported"
            self.level = CompositeId.Level.TWO
        else:  # base is of class: Id
            self.level = CompositeId.Level.ONE

        last_id = self._last_id()
        val = last_id + 1
        assert val <= self._max_value(self.level), ValueError("Exceeds max value")
        super().__init__(val, num_bytes=CompositeId.NUM_BYTES[self.level])
        self._set_last_id(val)

    def to_bytes(self) -> bytes:
        return self.base.to_bytes() + super().to_bytes()

    def __repr__(self) -> str:
        return CompositeId.__name__ + str(self)

    def __str__(self) -> str:
        return str(tuple(self._list_values()))

    def _list_values(self) -> list[int]:
        if isinstance(self.base, CompositeId):
            return self.base._list_values() + [self.val]
        return [self.base.val, self.val]

    def _last_id(self) -> int:
        msv = self._find_most_significant_value()
        return CompositeId._last_id_by_level[self.level]

    def _set_last_id(self, value):
        msv = self._find_most_significant_value()
        CompositeId._last_id_by_level[self.level] = value

    def _find_most_significant_value(self):
        base = self.base
        while isinstance(base, CompositeId):
            base = base.base
        return base.val
