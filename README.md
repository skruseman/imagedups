# imagedups

Locate image file duplicates across file systems. - Mar. 2026


## protobuf

- To compile .proto files:

  protoc --proto_path=. --python_out=. --pyi_out=. record.proto

  , which will generate record_pb2.py


## Usage

To use the tool, run the following command:

python imagedups.py --path /path/to/images
