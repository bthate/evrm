# This file is placed in the Public Domain.


"callback engine"


import queue
import threading
import _thread


from .error  import later
from .thread import launch


lock = threading.RLock()


class Reactor:

    def __init__(self):
        self.cbs     = {}
        self.queue   = queue.Queue()
        self.ready   = threading.Event()
        self.stopped = threading.Event()

    def callback(self, evt) -> None:
        with lock:
            func = self.cbs.get(evt.type, None)
            if not func:
                evt.ready()
                return
            try:
                evt._thr = launch(func, evt, name=evt.cmd)
            except Exception as ex:
                later(ex)
                evt.ready()

    def loop(self) -> None:
        while not self.stopped.is_set():
            evt = self.poll()
            if evt is None:
                break
            evt.orig = repr(self)
            try:
                self.callback(evt)
            except Exception as ex:
                later(ex)
                _thread.interrupt_main()
        self.ready.set()

    def poll(self):
        return self.queue.get()

    def put(self, evt) -> None:
        self.queue.put(evt)

    def register(self, typ, cbs) -> None:
        self.cbs[typ] = cbs

    def start(self) -> None:
        self.stopped.clear()
        self.ready.clear()
        launch(self.loop)

    def stop(self) -> None:
        self.stopped.set()
        self.queue.put(None)

    def wait(self) -> None:
        self.ready.wait()


def __dir__():
    return (
        'Reactor',
    )
