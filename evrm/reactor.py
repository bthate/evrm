# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R,W0212,W0718,E0402
# flake8: noqa


"reactor"


import queue
import ssl
import threading


from .error  import Error
from .event  import Event
from .thread import launch


class Reactor:

    errors = []

    def __init__(self):
        self.cbs = {}
        self.queue = queue.Queue()
        self.stopped = threading.Event()

    def announce(self, txt) -> None:
        self.raw(txt)

    @staticmethod
    def dispatch(func, evt) -> None:
        try:
            func(evt)
        except Exception as exc:
            Error.handle(exc)
            try:
                evt.ready()
            except AttributeError:
                pass

    def event(self, txt) -> Event:
        msg = Event()
        msg.type = 'event'
        msg.orig = repr(self)
        msg.txt = txt
        return msg

    def handle(self, evt) -> Event:
        func = self.cbs.get(evt.type, None)
        if func:
            evt._thr = launch(Reactor.dispatch, func, evt, name=evt.cmd or evt.type)
            evt._thr.join()
        return evt

    def loop(self) -> None:
        while not self.stopped.is_set():
            try:
                self.handle(self.poll())
            except (ssl.SSLError, EOFError) as ex:
                exc = ex.with_traceback(ex.__traceback__)
                Error.errors.append(exc)
                self.restart()

    def one(self, txt) -> Event:
        return self.handle(self.event(txt))

    def poll(self) -> Event:
        return self.queue.get()

    def put(self, evt) -> None:
        self.queue.put_nowait(evt)

    def raw(self, txt) -> None:
        pass

    def say(self, channel, txt) -> None:
        if channel:
            self.raw(txt)

    def register(self, typ, func) -> None:
        self.cbs[typ] = func

    def restart(self) -> None:
        self.stop()
        self.start()

    def start(self) -> None:
        launch(self.loop)

    def stop(self) -> None:
        self.stopped.set()
        self.queue.put_nowait(None)
