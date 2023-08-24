# This file is placed in the Public Domain.
#
# pylint: disable=C0115,C0116,W0212,W0718,E0402,W0201,W0613,E1120,R0902


"reactor"


import inspect
import queue
import ssl
import threading
import time


from .methods import parse
from .objects import Default, Object
from .threads import launch


def __dir__():
    return (
            'Broker',
            'Cfg',
            'Event',
            'Reactor',
            'command',
            'dispatch',
            "lsmod",
            'scan'
           )


Cfg = Default()


class Broker:

    objs = []

    @staticmethod
    def add(obj) -> None:
        Broker.objs.append(obj)

    @staticmethod
    def byorig(orig):
        for obj in Broker.objs:
            if object.__repr__(obj) == orig:
                return obj
        return None

    @staticmethod
    def bytype(typ):
        for obj in Broker.objs:
            if typ in object.__repr__(obj):
                return obj
        return None

    @staticmethod
    def remove(obj) -> None:
        try:
            Broker.objs.remove(obj)
        except ValueError:
            pass


class Event(Default):

    def __init__(self):
        Default.__init__(self)
        self._ready = threading.Event()
        self._thr = None
        self.result = []

    def ready(self) -> None:
        self._ready.set()

    def reply(self, txt) -> None:
        self.result.append(txt)

    def show(self):
        bot = Broker.byorig(self.orig)
        if bot:
            for txt in self.result:
                bot.say(self.channel, txt)

    def wait(self) -> []:
        if self._thr:
            self._thr.join()
        self._ready.wait()
        return self.result


class Reactor(Object):

    errors = []
    output = print

    def __init__(self):
        Object.__init__(self)
        self.cbs = {}
        self.queue = queue.Queue()
        self.stopped = threading.Event()

    def event(self, txt) -> Event:
        msg = Event()
        msg.type = 'event'
        msg.orig = object.__repr__(self)
        msg.txt = txt
        return msg

    def handle(self, evt):
        func = self.cbs.get(evt.type, None)
        if func:
            evt._thr = launch(
                              dispatch,
                              func,
                              evt,
                              name=evt.cmd or evt.type
                             )
        return evt

    def loop(self) -> None:
        while not self.stopped.is_set():
            try:
                evt = self.poll()
                if evt is None:
                    self.stopped.set()
                    continue
                self.handle(evt)
            except (ssl.SSLError, EOFError) as ex:
                exc = ex.with_traceback(ex.__traceback__)
                self.errors.append(exc)
                self.stop()
                self.start()

    def poll(self):
        return self.queue.get()

    def put(self, evt) -> None:
        self.queue.put_nowait(evt)

    def register(self, typ, func) -> None:
        self.cbs[typ] = func

    def start(self):
        launch(self.loop)

    def stop(self):
        self.stopped.set()
        self.put(None)


class Client(Reactor):

    cmds = {}
    skip = ["PING", "PONG"]

    def __init__(self):
        Reactor.__init__(self)
        self.register("command", command)
        Broker.add(self)

    @staticmethod
    def add(func):
        Client.cmds[func.__name__] = func

    def announce(self, txt):
        self.raw(txt)

    @staticmethod
    def debug(txt):
        if "v" in Cfg.opts and Client.output is not None:
            donext = False
            for skp in Client.skip:
                if skp in txt:
                    donext = True
            if donext:
                return
            Client.output(txt)

    def raw(self, txt):
        pass

    def say(self, channel, txt):
        self.raw(txt)

    @staticmethod
    def scan(mod) -> None:
        for key, cmd in inspect.getmembers(mod, inspect.isfunction):
            if key.startswith("cb"):
                continue
            if 'event' in cmd.__code__.co_varnames:
                Client.add(cmd)

    def wait(self):
        while not self.stopped.is_set():
            time.sleep(1.0)


def command(evt):
    parse(evt, evt.txt)
    func = Client.cmds.get(evt.cmd, None)
    if func:
        try:
            func(evt)
            evt.show()
        except Exception as ex:
            exc = ex.with_traceback(ex.__traceback__)
            Client.errors.append(exc)
    evt.ready()


def dispatch(func, evt) -> None:
    try:
        func(evt)
    except Exception as exc:
        excp = exc.with_traceback(exc.__traceback__)
        Reactor.errors.append(excp)
        try:
            evt.ready()
        except AttributeError:
            pass
