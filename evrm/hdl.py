# This file is placed in the Public Domain.

import queue
import threading

from .bus import Bus
from .evt import Command, Event
from .obj import Object, getname, getmain
from .thr import launch
from .trc import get_exception

class Error(Event):

    pass


class Restart(Exception):

    pass


class Stop(Exception):

    pass


class Break(Exception):

    pass


class ENotImplemented(Exception):

    pass


class Dispatcher(Object):

    def __init__(self):
        super().__init__()
        self.cbs = Object()

    def dispatch(self, event):
        if event and event.type in self.cbs:
            self.cbs[event.type](self, event)
        else:
            event.ready()

    def register(self, k, v):
        self.cbs[str(k)] = v


class Loop(Object):

    def __init__(self):
        super().__init__()
        self.queue = queue.Queue()
        self.speed = "normal"
        self.stopped = threading.Event()

    def do(self, e):
        k = getmain("k")
        k.dispatch(e)

    def error(self, txt):
        pass

    def loop(self):
        dorestart = False
        self.stopped.clear()
        while not self.stopped.isSet():
            e = self.queue.get()
            try:
                self.do(e)
            except Restart:
                dorestart = True
                break
            except Stop:
                break
            except Exception:
                self.error(get_exception())
        if dorestart:
            self.restart()

    def restart(self):
        self.stop()
        self.start()

    def put(self, e):
        self.queue.put_nowait(e)

    def start(self):
        launch(self.loop)
        return self

    def stop(self):
        self.stopped.set()
        self.queue.put(None)


class Handler(Dispatcher, Loop):

    def __init__(self):
        Dispatcher.__init__(self)
        Loop.__init__(self)

    def event(self, txt):
        if txt is None:
            return None
        c = Command()
        c.txt = txt or ""
        c.orig = self.__oqn__()
        return c

    def handle(self, clt, e):
        k = getmain("k")
        if k:
            k.put(e)

    def loop(self):
        while not self.stopped.isSet():
            try:
                txt = self.poll()
            except (ConnectionRefusedError, ConnectionResetError) as ex:
                self.error(str(ex))
                break
            if txt is None:
                self.error("%s stopped" % getname(self))
                break
            e = self.event(txt)
            if not e:
                self.error("%s stopped" % getname(self))
                return
            self.handle(self, e)

    def poll(self):
        return self.queue.get()

    def start(self):
        super().start()
        Bus.add(self)
