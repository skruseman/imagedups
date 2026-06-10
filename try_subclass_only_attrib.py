""" Demonstrates ... """

from __future__ import annotations

from typing import cast


class Id:

    def __init__(self, val: int):
        self.val = val


class CompositeId(Id):

    def __init__(self, base: Id):
        level = 1
        if isinstance(base, CompositeId):
            level = base.level + 1
        self._ini(base, _val=42, _level=level)

    def _ini(self, base: Id, _val: int, _level: int):
        self.base = base
        self.level = _level
        super().__init__(_val)


    @classmethod
    def intern(cls, base: Id, val: int, level: int) -> CompositeId:
        cid = cls.__new__(cls)
        cid._ini(base, val, level)
        return cid


rid = Id(7)
did = CompositeId(rid)
print(rid.val, did.val, did.level, did.base.val)  # 7, 42, 1, 7
fid = CompositeId.intern(did, 43, 2)
print(fid.val, fid.level)  # 43, 2
if isinstance(fid.base, CompositeId):
    print(did.base.val, fid.base.val, fid.base.base.val)  # 7, 42, 7
# did2 = CompositeId(fid, _val=43, _level=2)