from __future__ import annotations

from typing import Any, cast


class Id:
    """Integer valued identifier objects of small, fixed byte size which makes them
    suitable for storage in a small number of bytes.

    Values are provided by the user and should be positive integers (>= 0)
    less than 256**N, where N is the preset number of bytes. Attempts to create an identifier
    with an int value that doesn't fit in N bytes, will raise an exception.

    Identifiers are considered immutable and can be used as dict keys:
    equality testing and hashing are supported.
    """

    NUM_BYTES = 2

    @staticmethod
    def from_bytes(byte_str: bytes) -> Id:
        """Creates a new instance from the provided bytes object."""
        if len(byte_str) > Id.NUM_BYTES:
            raise ValueError(
                f'Byte string too long; {len(byte_str)} instead of {Id.NUM_BYTES} bytes')
        return Id(int.from_bytes(byte_str))

    def __init__(self, val: int):
        """Creates an identifier object for the specified integer value."""
        super().__init__()
        assert val.to_bytes(length=Id.NUM_BYTES)
        self.val = val

    def to_bytes(self) -> bytes:
        return self.val.to_bytes(length=self.NUM_BYTES)

    def to_hex(self) -> str:
        return self.to_bytes().hex()

    def __repr__(self) -> str:
        return self.__class__.__name__ + f'({self})'

    def __str__(self) -> str:
        return str(self.val)

    def __eq__(self, other: Id) -> bool:
        if type(other) is not type(self):  # be strict: prevent matching Id with CompositeId
            return NotImplemented
        return self.val == other.val

    def __hash__(self) -> int:
        return hash(self.val)


class CompositeId(Id):
    """Identifier objects consisting of a sequence of integer values, each of
    small, fixed byte size, making the object suitable for storage in a fixed
    number of bytes.

    A composite identifier is derived from a base identifier which can be either
    an Id instance or another CompositeId instance.

    Each level of composing integer values can be of different (but preset) size.
    The integer value of any level must fit in the level's preset number of bytes.

    Each component value fits a fixed number of bytes N, with the highest value being: 256**N - 1.
    The number of bytes per value is defined in this class, and can differ from level to level;
    if not defined than a default length is used.
    For number of bytes for the most significant component value see class Id.

    Values generated are positive identifiers starting at 1 and incremented with each new
    identifier for the same base.
    """

    DEFAULT_NUM_BYTES = 2

    NUM_BYTES_BY_LEVEL = {
        # 1: 2,
        2: 2,
    }

    _last_value_by_base = {}

    @classmethod
    def from_bytes(cls, byte_str: bytes) -> Id:
        """Creates a new instance from the provided bytes.

        This will not touch the class' internal registry of last used partial ID values.
        So, if after generating CompositeId(42, 1) you construct from bytes CompositeId(42, 7),
        the next generated CompositeId will simply become (42, 2).
        """
        first_part_bytes = byte_str[:super().NUM_BYTES]
        remaining_bytes = byte_str[super().NUM_BYTES:]
        parts_bytes = [first_part_bytes]
        level = 1

        id_ = super().from_bytes(first_part_bytes)

        while remaining_bytes:
            num_bytes = CompositeId.NUM_BYTES_BY_LEVEL.get(level, CompositeId.DEFAULT_NUM_BYTES)
            if len(remaining_bytes) < num_bytes:
                raise ValueError(
                    f'Level {level} partial ID values require {num_bytes} bytes; '
                    f'got only {len(remaining_bytes)}')
            value = int.from_bytes(remaining_bytes[:num_bytes])
            base, id_ = id_, cls.__new__(cls)
            id_._initialize(base, value, level)
            remaining_bytes = remaining_bytes[num_bytes:]
            level += 1
        return id_

    @classmethod
    def _bytes_to_parts_bytes(cls, byte_str: bytes) -> tuple[bytes, ...]:
        """Creates from a bytes object a tuple of bytes objects representing component values
        of a CompositeId object."""
        index = super().NUM_BYTES
        parts = [byte_str[:index]]
        remaining_bytes = byte_str[index:]
        level = 1
        while remaining_bytes:
            index = cls.NUM_BYTES_BY_LEVEL.get(level, cls.DEFAULT_NUM_BYTES)
            if len(remaining_bytes) < index:
                raise ValueError(
                    f'Level {level} partial ID values require {index} bytes; '
                    f'got only {len(remaining_bytes)}')
            parts.append(remaining_bytes[:index])
            remaining_bytes = remaining_bytes[index:]
            level += 1
        return tuple(parts)

    @classmethod
    def bytes_to_parts(cls, byte_str: bytes) -> tuple[int, ...]:
        """Converts a bytes object into a list of integers representing component values"""
        parts_bytes = cls._bytes_to_parts_bytes(byte_str)
        return tuple(int.from_bytes(part) for part in parts_bytes)


    def __init__(self, base: Id):
        """
        Creates a new instance, adding a component level with respect to the
        specified identifier that is considered the new instance's base.

        The value for the new component is generated based
        on the class' registry of highest issued value for each base identifier.
        First issued value (per base) is always 1, then 2, etc..
        This provides a basic and temporary level of uniqueness; the registry starts
        fresh in each python session.

        Example:

        id_1 = Id(42)             #  42
        id_2 = CompositeId(id_1)  # (42, 1)
        id_3 = CompositeId(id_1)  # (42, 2)
        id_4 = CompositeId(id_3)  # (42, 2, 1)
        """

        self.level = 1
        if isinstance(base, CompositeId):
            self.level = base.level + 1

        base_hex = base.to_hex()
        value = self._last_value_by_base.get(base_hex, 0) + 1
        num_bytes = self.NUM_BYTES_BY_LEVEL.get(self.level, self.DEFAULT_NUM_BYTES)
        # assert value < 2 ** (num_bytes * 8)
        assert int.to_bytes(value, num_bytes)
        self._last_value_by_base[base_hex] = value
        self._initialize(base, value, self.level)

    def _initialize(self, base: Id, value: int, level: int):
        super().__init__(value)
        self.base = base
        self.level = level


    def parts(self) -> tuple[int, ...]:
            """Returns the component values of the identifier as a tuple."""
            return tuple(self._parts())

    def _parts(self) -> list[int]:
        """Returns the component values of the identifier as a list."""
        base = self.base
        parts = base._parts() if isinstance(base, CompositeId) else [base.val]
        parts.append(self.val)
        return parts

    def to_bytes(self) -> bytes:
        return self.base.to_bytes() + super().to_bytes()

    def __repr__(self) -> str:
        return CompositeId.__name__ + str(self)

    def __str__(self) -> str:
        return str(self.parts())

    def __eq__(self, other: CompositeId) -> bool:
        if not isinstance(other, CompositeId):
            return NotImplemented
        return (self.base, self.val) == (other.base, other.val)

    def __hash__(self) -> int:
        return hash((self.base, self.val))
