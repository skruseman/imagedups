from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class RunRecord(_message.Message):
    __slots__ = ["schema_version", "path", "description", "platform", "date_time", "dur_secs", "status", "num_dirs", "num_files", "extra", "error"]
    class ExtraEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    SCHEMA_VERSION_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PLATFORM_FIELD_NUMBER: _ClassVar[int]
    DATE_TIME_FIELD_NUMBER: _ClassVar[int]
    DUR_SECS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    NUM_DIRS_FIELD_NUMBER: _ClassVar[int]
    NUM_FILES_FIELD_NUMBER: _ClassVar[int]
    EXTRA_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    schema_version: int
    path: str
    description: str
    platform: str
    date_time: float
    dur_secs: float
    status: str
    num_dirs: int
    num_files: int
    extra: _containers.ScalarMap[str, str]
    error: str
    def __init__(self, schema_version: _Optional[int] = ..., path: _Optional[str] = ..., description: _Optional[str] = ..., platform: _Optional[str] = ..., date_time: _Optional[float] = ..., dur_secs: _Optional[float] = ..., status: _Optional[str] = ..., num_dirs: _Optional[int] = ..., num_files: _Optional[int] = ..., extra: _Optional[_Mapping[str, str]] = ..., error: _Optional[str] = ...) -> None: ...
