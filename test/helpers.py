import contextlib
import threading


@contextlib.contextmanager
def threaded(func, *args):
    t = threading.Thread(target=func, args=args)
    t.start()
    yield
    t.join()

