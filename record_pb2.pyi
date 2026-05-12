from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class RunRecord(_message.Message):
    __slots__ = ["schema_version", "id", "path", "description", "platform", "date_time", "dur_secs", "status", "root_id", "num_dirs", "num_files", "extra", "error"]
    class ExtraEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    SCHEMA_VERSION_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PLATFORM_FIELD_NUMBER: _ClassVar[int]
    DATE_TIME_FIELD_NUMBER: _ClassVar[int]
    DUR_SECS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ROOT_ID_FIELD_NUMBER: _ClassVar[int]
    NUM_DIRS_FIELD_NUMBER: _ClassVar[int]
    NUM_FILES_FIELD_NUMBER: _ClassVar[int]
    EXTRA_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    schema_version: int
    id: int
    path: str
    description: str
    platform: str
    date_time: float
    dur_secs: float
    status: str
    root_id: int
    num_dirs: int
    num_files: int
    extra: _containers.ScalarMap[str, str]
    error: str
    def __init__(self, schema_version: _Optional[int] = ..., id: _Optional[int] = ..., path: _Optional[str] = ..., description: _Optional[str] = ..., platform: _Optional[str] = ..., date_time: _Optional[float] = ..., dur_secs: _Optional[float] = ..., status: _Optional[str] = ..., root_id: _Optional[int] = ..., num_dirs: _Optional[int] = ..., num_files: _Optional[int] = ..., extra: _Optional[_Mapping[str, str]] = ..., error: _Optional[str] = ...) -> None: ...

class DirRecord(_message.Message):
    __slots__ = ["schema_version", "run_id", "id", "parent_id", "path", "date_time", "all_hash", "files_hash", "dirs_hash", "num_entries", "dir_id", "file_id"]
    SCHEMA_VERSION_FIELD_NUMBER: _ClassVar[int]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    PARENT_ID_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    DATE_TIME_FIELD_NUMBER: _ClassVar[int]
    ALL_HASH_FIELD_NUMBER: _ClassVar[int]
    FILES_HASH_FIELD_NUMBER: _ClassVar[int]
    DIRS_HASH_FIELD_NUMBER: _ClassVar[int]
    NUM_ENTRIES_FIELD_NUMBER: _ClassVar[int]
    DIR_ID_FIELD_NUMBER: _ClassVar[int]
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    schema_version: int
    run_id: int
    id: int
    parent_id: int
    path: str
    date_time: float
    all_hash: bytes
    files_hash: bytes
    dirs_hash: bytes
    num_entries: int
    dir_id: _containers.RepeatedScalarFieldContainer[int]
    file_id: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, schema_version: _Optional[int] = ..., run_id: _Optional[int] = ..., id: _Optional[int] = ..., parent_id: _Optional[int] = ..., path: _Optional[str] = ..., date_time: _Optional[float] = ..., all_hash: _Optional[bytes] = ..., files_hash: _Optional[bytes] = ..., dirs_hash: _Optional[bytes] = ..., num_entries: _Optional[int] = ..., dir_id: _Optional[_Iterable[int]] = ..., file_id: _Optional[_Iterable[int]] = ...) -> None: ...

class FileRecord(_message.Message):
    __slots__ = ["schema_version", "run_id", "id", "name", "dir_id", "date_time", "length", "hash"]
    SCHEMA_VERSION_FIELD_NUMBER: _ClassVar[int]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DIR_ID_FIELD_NUMBER: _ClassVar[int]
    DATE_TIME_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    schema_version: int
    run_id: int
    id: int
    name: str
    dir_id: int
    date_time: float
    length: int
    hash: bytes
    def __init__(self, schema_version: _Optional[int] = ..., run_id: _Optional[int] = ..., id: _Optional[int] = ..., name: _Optional[str] = ..., dir_id: _Optional[int] = ..., date_time: _Optional[float] = ..., length: _Optional[int] = ..., hash: _Optional[bytes] = ...) -> None: ...
