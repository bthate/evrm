# This file is placed in the Public Domain.

"handler"

from .bus import Bus
from .err import ENOMORE, ENOTIMPLEMENTED
from .evt import Event
from .ldr import Loader
from .obj import Object
from .thr import launch
from .trc import exception
from .utl import cprint, locked
from .zzz import queue, time, _thread, threading

class Handler(Loader):

    def __init__(self, val=None):
        super().__init__(val)
        self.cbs = Object()
        self.queue = queue.Queue()
        self.stopped = False
        self.register("end", end)

    def callbacks(self, event):
        if event and event.type in self.cbs:
            self.cbs[event.type](self, event)

    def error(self, ex):
        print(ex)

    def handler(self):
        while not self.stopped:
            e = self.queue.get()
            try:
                self.callbacks(e)
            except ENOMORE:
                break
            except Exception as ex:
                self.error(ex)

    def put(self, e):
        self.queue.put_nowait(e)

    def register(self, name, callback):
        self.cbs[name] = callback

    def restart(self):
        self.stop()
        time.sleep(5.0)
        self.start()

    def start(self):
        self.stopped = False
        launch(self.handler)
        return self

    def stop(self):
        self.stopped = True
        e = Event()
        e.type = "end"
        self.queue.put(e)

def cmd(hdl, obj):
    obj.parse()
    f = hdl.cmd(obj.cmd)
    res = None
    if f:
        res = f(obj)
        obj.show()
    obj.ready()
    return res

def end(hdl, obj):
    raise ENOMORE("bye!")
