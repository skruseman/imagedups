from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class UserRecord(_message.Message):
    __slots__ = ["schema_version", "user_id", "name", "email", "tags", "updated_unix_ts"]
    SCHEMA_VERSION_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    UPDATED_UNIX_TS_FIELD_NUMBER: _ClassVar[int]
    schema_version: int
    user_id: str
    name: str
    email: str
    tags: _containers.RepeatedScalarFieldContainer[str]
    updated_unix_ts: int
    def __init__(self, schema_version: _Optional[int] = ..., user_id: _Optional[str] = ..., name: _Optional[str] = ..., email: _Optional[str] = ..., tags: _Optional[_Iterable[str]] = ..., updated_unix_ts: _Optional[int] = ...) -> None: ...
