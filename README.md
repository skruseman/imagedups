# imagedups

Locate image file duplicates across file systems. - Mar. 2026


## protobuf

- To compile .proto files:

  protoc --proto_path=. --python_out=. --pyi_out=. record.proto

  , which will generate record_pb2.py


## Usage

To use the tool, run the following command:

python imagedups.py --path /path/to/images


## Design motivation

- lmdb: to learn, fast, in combi with protobuf
- protobuf: to learn
- multi-threading: to learn, optimize for cpu tasks (hashing) and
  IO tasks (file system walk, reading for hashing, writing the DB)
- monitoring thread: learn, progress reporting during long runs
- don't keep objects for every file and dir in memory during runs;
  objects (especially for files) to become GC-able immediately
  after stored in the DB; use of threading.Queue for multi-threading
  push-back on producers (preventing over-production if hashing and storage
  are slow).
- xxhash: to learn

### lmdb table and index design

Note: I don't have a clear view on query types I'll need up front;
mostly only those for actual duplicate (hashes search).

- Collect file hashes across runs for unrelated file systems
  (laptop disks, usb disks, pc disk): find file duplicates across
  different file systems.
- Directory hashing:
  - Find directories with exact same file contents (exact same files)
    ; both for files local to a dir and accumulated across subdirs.
- File hashes must be solid (no collisions) hence sha256: 
  false positive analysis requires manual inspection, possibly
  rehashing (with alt. hash algo)
- Dir hash collisions are less severe hence xxhash 64bit; false positive
  analysis requires just comparing file hashes, file names, file timestamps.
- Grouping records by run ID: faster retrieve of run related records (compare with
  ordering by uuid4 only)
