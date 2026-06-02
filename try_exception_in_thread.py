import threading
import time
import sys

fatal_error = threading.Event()

def worker():
    print("worker 1 started")
    time.sleep(1)
    if True:
        fatal_error.set()
        print("worker 1 aborting due to fatal error")
        raise ValueError("boom")
    print("worker 1 ends normally")

def worker2():
    print("worker 2 started")
    for _ in range(5):
        time.sleep(1)
        if fatal_error.is_set():
            print("worker 2 aborts")
            return
    print("worker 2 is done and exits now")

t2 = threading.Thread(target=worker2, name="worker2")
t2.start()

t = threading.Thread(target=worker, name="worker1")
t.start()

print("main continues")

t2.join()
t.join()

print("program still alive: it didn't run into any exception")

if fatal_error.is_set():
    print("program exits in error (but gracefully) since to fatal error flag is set")
    sys.exit(1)

print("program exits normally")
