from __future__ import annotations

class Id:
    """Provides identifiers fitting a fixed number of bytes.

    Values are provided by the user and should be positive integers > 1 and
    < 256**N where N is the number of bytes.
    Uniqueness is not supported; if so desired, it is the responsibility of the user.
    Specialized testing for equality of instances is not supported.
    """

    NUM_BYTES = 2

    def __init__(self, val: int):
        self.num_bytes = Id.NUM_BYTES
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
    adding a value to the provided base identifier. E.g.:

    Values generated are positive identifiers starting at 1, incrementing with each identifier.

    id_1 = Id(42)             #  42
    id_2 = CompositeId(id_1)  # (42, 1)
    id_3 = CompositeId(id_1)  # (42, 2)
    id_4 = CompositeId(id_3)  # (42, 2, 1)

    Each generated identifier will be unique with respect to its base.
    This uniqueness applies only to a single python session.

    Each component value fits a fixed number of bytes N, with the highest value being: 256**N - 1.
    The number of bytes per value is defined in this class, and can differ from level to level;
    if not defined than a default length is used.
    For number of bytes for the most significant component value see class Id.
    Specialized testing for equality of instances is not supported.
    """

    # class Level(Enum):
    #     """Nesting level (relative to base identifier)."""
    #     ONE = 1
    #     TWO = 2

    DEFAULT_NUM_BYTES = 2

    NUM_BYTES_BY_LEVEL = {
        1: 2,
        2: 2,  # used to be 4
    }

    # _latest_id_by_level = {
    #     Level.ONE: 0,
    #     Level.TWO: 0,
    # }

    # for Level.One parts, the key is a 4 hexit string
    # for Level.Two parts, the key is an 8 hexit string
    _last_value_by_base = {}

    # @staticmethod
    # def _max_value(level: CompositeId.Level) -> int:
    #     return 256**CompositeId.NUM_BYTES[level] - 1

    def __init__(self, base: Id):
        self.base = base
        self.level = 1
        if isinstance(base, CompositeId):
            self.level = base.level + 1

        key = self.base.to_hex()
        last_value = CompositeId._last_value_by_base.get(key, 0)
        new_value = last_value + 1
        num_bytes = CompositeId.NUM_BYTES_BY_LEVEL.get(self.level, CompositeId.DEFAULT_NUM_BYTES)
        assert new_value < 2**num_bytes
        super().__init__(new_value)
        CompositeId._last_value_by_base[key] = new_value

        # last_value = self._latest_id()
        # new_value = last_value + 1
        # assert new_value <= self._max_value(self.level), ValueError("Exceeds max value")
        # super().__init__(new_value, num_bytes=num_bytes)
        # self._set_last_id(new_value)

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

    # def _latest_id(self) -> int:
    #     # msv = self._find_most_significant_value()
    #     return CompositeId._latest_id_by_level[self.level]
    #
    # def _set_last_id(self, value):
    #     # msv = self._find_most_significant_value()
    #     CompositeId._latest_id_by_level[self.level] = value

    # def _find_most_significant_value(self):
    #     base = self.base
    #     while isinstance(base, CompositeId):
    #         base = base.base
    #     return base.val
