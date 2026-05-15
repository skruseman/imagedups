from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class RunRecord(_message.Message):
    __slots__ = ["schema_version", "id", "uuid", "path", "description", "platform", "start_time", "dur_secs", "status", "root_id", "num_dirs", "num_files", "extra", "error", "tags"]
    class ExtraEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    SCHEMA_VERSION_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PLATFORM_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    DUR_SECS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ROOT_ID_FIELD_NUMBER: _ClassVar[int]
    NUM_DIRS_FIELD_NUMBER: _ClassVar[int]
    NUM_FILES_FIELD_NUMBER: _ClassVar[int]
    EXTRA_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    schema_version: int
    id: int
    uuid: bytes
    path: str
    description: str
    platform: str
    start_time: float
    dur_secs: float
    status: str
    root_id: bytes
    num_dirs: int
    num_files: int
    extra: _containers.ScalarMap[str, str]
    error: str
    tags: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, schema_version: _Optional[int] = ..., id: _Optional[int] = ..., uuid: _Optional[bytes] = ..., path: _Optional[str] = ..., description: _Optional[str] = ..., platform: _Optional[str] = ..., start_time: _Optional[float] = ..., dur_secs: _Optional[float] = ..., status: _Optional[str] = ..., root_id: _Optional[bytes] = ..., num_dirs: _Optional[int] = ..., num_files: _Optional[int] = ..., extra: _Optional[_Mapping[str, str]] = ..., error: _Optional[str] = ..., tags: _Optional[_Iterable[str]] = ...) -> None: ...

class DirRecord(_message.Message):
    __slots__ = ["schema_version", "id", "parent_id", "path", "date_time", "files_hash", "dirs_hash", "file_ids", "dir_ids", "tags"]
    SCHEMA_VERSION_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    PARENT_ID_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    DATE_TIME_FIELD_NUMBER: _ClassVar[int]
    FILES_HASH_FIELD_NUMBER: _ClassVar[int]
    DIRS_HASH_FIELD_NUMBER: _ClassVar[int]
    FILE_IDS_FIELD_NUMBER: _ClassVar[int]
    DIR_IDS_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    schema_version: int
    id: bytes
    parent_id: bytes
    path: str
    date_time: float
    files_hash: str
    dirs_hash: str
    file_ids: _containers.RepeatedScalarFieldContainer[bytes]
    dir_ids: _containers.RepeatedScalarFieldContainer[bytes]
    tags: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, schema_version: _Optional[int] = ..., id: _Optional[bytes] = ..., parent_id: _Optional[bytes] = ..., path: _Optional[str] = ..., date_time: _Optional[float] = ..., files_hash: _Optional[str] = ..., dirs_hash: _Optional[str] = ..., file_ids: _Optional[_Iterable[bytes]] = ..., dir_ids: _Optional[_Iterable[bytes]] = ..., tags: _Optional[_Iterable[str]] = ...) -> None: ...

class FileRecord(_message.Message):
    __slots__ = ["schema_version", "id", "name", "date_time", "length", "hash", "tags"]
    SCHEMA_VERSION_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DATE_TIME_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    schema_version: int
    id: bytes
    name: str
    date_time: float
    length: int
    hash: str
    tags: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, schema_version: _Optional[int] = ..., id: _Optional[bytes] = ..., name: _Optional[str] = ..., date_time: _Optional[float] = ..., length: _Optional[int] = ..., hash: _Optional[str] = ..., tags: _Optional[_Iterable[str]] = ...) -> None: ...
