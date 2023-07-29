# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R,W0212,W0718,E0402
# flake8: noqa


"thread"


import functools
import queue
import threading
import time


from .error import Error
from .utils import name


class Thread(threading.Thread):

    ""

    def __init__(self, func, thrname, *args, daemon=True):
        super().__init__(None, self.run, thrname, (), {}, daemon=daemon)
        self._result = None
        self.name = thrname or name(func)
        self.queue = queue.Queue()
        self.queue.put_nowait((func, args))
        self.sleep = None
        self.starttime = time.time()

    def __iter__(self):
        return self

    def __next__(self):
        for k in dir(self):
            yield k

    def join(self, timeout=None):
        ""
        super().join(timeout)
        return self._result

    def run(self):
        ""
        func, args = self.queue.get()
        try:
            self._result = func(*args)
        except Exception as ex:
            exc = ex.with_traceback(ex.__traceback__)
            Error.errors.append(exc)
            if args:
                try:
                    args[0].ready()
                except AttributeError:
                    pass


def launch(func, *args, **kwargs) -> Thread:
    thrname = kwargs.get('name', '')
    thread = Thread(func, thrname, *args)
    thread.start()
    return thread


def threaded(func, *args, **kwargs) -> None:

    @functools.wraps(func)
    def threadedfunc(*args, **kwargs):
        thread = launch(func, *args, **kwargs)
        if args:
            args[0].thr = thread
        return thread

    threadedfunc.args = args
    threadedfunc.kwargs = kwargs

    return threadedfunc
