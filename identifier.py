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
        if isinstance(sup, CompositeId):
            assert sup.level == CompositeId.Level.ONE, "Nesting beyond two sub-levels is not supported"
            self.level = CompositeId.Level.TWO
        else:  # sup is of class: Id
            self.level = CompositeId.Level.ONE

        last_id = CompositeId._last_id_by_level[self.level]
        val = last_id + 1
        assert val <= self.LEVEL_SIZES[self.level]["max_value"], ValueError("Exceeds max value")
        super().__init__(val, num_bytes=CompositeId.LEVEL_SIZES[self.level]["num_bytes"])
        CompositeId._last_id_by_level[self.level] = val

    def to_bytes(self) -> bytes:
        return self.sup.to_bytes() + super().to_bytes()

    def __repr__(self) -> str:
        return self.__class__.__name__ + str(self)

    def __str__(self) -> str:
        return str(tuple(self._list_values()))

    def _list_values(self) -> list[int]:
        if isinstance(self.sup, CompositeId):
            return self.sup._list_values() + [self.val]
        return [self.sup.val, self.val]
