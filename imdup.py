import hashlib
import os
import uuid
from typing import Optional


RUN_ID = 42

last_id: int = 0
last_hash: int = 0

start_dir = 'C:\\Users\\skrus\\Dropbox\\tuin'

dirs_by_path = dict()


# generate run ID as yyyyMMdd:hhmmssuuu of start (wall) time

# run record: date and time, OS spec, FS spec, user comment
#             run duration,
#             total num files hashes, total num dir hashes,
#             errors encountered?
#             root dir ID?

def generate_id() -> str:
    global last_id
    last_id += 1
    # return str(uuid.uuid4())
    return f'id_{('000' + str(last_id))[-4:]}'

def hash_file(path: str) -> str:
    global last_hash
    last_hash += 1
    return f'hash_{('000' + str(last_hash))[-4:]}'

def handle_dir(path: str, subdirs: list[str], files: list[str]):
    print(f'Handling dir {path}')
    dir = dict()
    dir['run_id'] = RUN_ID
    dir['id'] = generate_id()
    dir['path'] = path
    dir['subdirs'] = sorted(subdirs)
    dir['files'] = sorted(files)

    subdir_hashes = []
    for subdir_name in dir['subdirs']:
        subdir_path = os.path.join(path, subdir_name)
        subdir = dirs_by_path[subdir_path]
        subdir_hashes.append(subdir['hash'])  # same order as subdir names

    file_hashes = []
    for file in dir['files']:
        file_path = os.path.join(path, file)
        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
            file_hashes.append(file_hash)  # same order a file names
            # now store the file hash and file record

    # calculate hash of concatenated file hashes
    files_hash_input = ''.join(sorted(file_hashes))
    files_hash = hashlib.md5(files_hash_input.encode()).hexdigest()

    # concat the subdir hashes
    subdirs_hash_input = ''.join(sorted(subdir_hashes))
    subdirs_hash = hashlib.md5(subdirs_hash_input.encode()).hexdigest()

    dir['hash'] = files_hash + '::' + subdirs_hash
    return dir

def create_dir_info(path: str, dirs: list[str]):
    pass
    return None

def main() -> None:
    for root, dirs, files in os.walk(start_dir, topdown=False):
        dirs_by_path[root] = handle_dir(root, dirs, files)

    # walk the flattened dir tree where each dir can access values
    # (hashes) of its subdirs
    a: Optional[list] = None
    for dir_obj in a:
        pass

        # generate dir ID (if not already)
        # include the run ID

        # dir ID entry:
        # - key is dirid:
        # - record: run ID, dir name, file contents hash,
        #           dir path, contained file ID's,
        #           contained dir ID's

        # involve the dir name
        # involve the number of contained files?
        # involve ordered list of contained file names?
        # involve ordered list of contained dir names?
        # include into record the contained file ID's
        # include into record the contained dir ID's

        # create files contents hash:
        # - collect the file hashes
        # - concat these hashes in alphan order
        # - hash the resulting string

        # create files names hash:
        # - collect the file names
        # - concat these names in alphan order
        # - hash the resulting string

        # to be stored as: dir:<file contents hash>:<file names has>:<dir ID>

        # to create the dir hash, I need;
        #   - list of hashes of files it contains
        #   - list of hashes of dirs it contains
        # concat the hashes in normalized order (e.g. lexicogr)


if __name__ == "__main__":
    main()
