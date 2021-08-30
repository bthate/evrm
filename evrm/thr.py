# This file is placed in the Public Domain

import queue
import threading

from .obj import getname

class Thr(threading.Thread):

    def __init__(self, func, *args, thrname="", daemon=True):
        super().__init__(None, self.run, thrname, (), {}, daemon=daemon)
        self.name = thrname or getname(func)
        self.result = None
        self.queue = queue.Queue()
        self.queue.put_nowait((func, args))
        self.sleep = 0

    def __iter__(self):
        return self

    def __next__(self):
        for k in dir(self):
            yield k

    def join(self, timeout=None):
        super().join(timeout)
        return self.result

    def run(self):
        func, args = self.queue.get_nowait()
        if args:
            target = vars(args[0])
            if target and "txt" in dir(target):
                self.name = target.txt.split()[0]
        self.setName(self.name)
        self.result = func(*args)


def launch(func, *args, **kwargs):
    name = kwargs.get("name", getname(func))
    t = Thr(func, *args, thrname=name, daemon=True)
    t.start()
    return t
