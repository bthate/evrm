# This file is in the Public Domain.

"clients"

from .bus import Bus
from .err import ENOTIMPLEMENTED
from .evt import Command
from .hdl import Handler, cmd
from .itr import findcmds
from .itr import scan as iscan
from .obj import Cfg, Object
from .prs import parseargs
from .thr import launch
from .trc import exception
from .utl import cprint
from .zzz import os, queue, sys, threading, time, _thread

verbose = False

class Cfg(Cfg):

    def __init__(self):
        super().__init__(self)
        self.name = "botl"

class Client(Handler):

    def __init__(self, val=None):
        super().__init__(val)
        self.cfg = Cfg()
        self.iqueue = queue.Queue()
        self.finalize(val)

    def announce(self, txt):
        pass

    def dosay(self, channel, txt):
        cprint(txt)

    def error(self, ex):
        self.restart()

    def event(self, txt):
        return Command({"txt": txt, "orig": repr(self)})

    def finalize(self, val):
        pass

    def input(self):
        while not self.stopped:
            e = self.once()
            self.pre(e)
            self.put(e)
            self.post(e)

    def once(self):
        txt = self.poll()
        e = self.event(txt)
        return e

    def op(self, ops):
        for opt in ops:
            if opt in self.cfg.opts:
                return True
        return False

    def parse(self, wd=None):
        import botl.obj
        parseargs(self.cfg, " ".join(sys.argv[1:]))
        self.cfg.update(self.cfg.sets or {})
        if self.op("v"):
            self.cfg.verbose = True
        botl.obj.wd = self.cfg.wd = wd or self.cfg.wd or os.path.expanduser("~/.%s" % self.cfg.name)
        return self

    def pre(self, e):
        pass

    def poll(self):
        return self.iqueue.get()

    def post(self, e):
        pass

    def start(self):
        super().start()
        launch(self.input)

    def stop(self):
        super().stop()
        self.stopped = True
        self.iqueue.put_nowait("")

    def wait(self):
        while not self.stopped:
            time.sleep(30.0)

class CLI(Client):

    def dosay(self, channel, txt):
        print(txt)

    def finalize(self, val):
        self.addbus()
        self.register("cmd", cmd)

    def run(self, txt=None, check=False):
        txt = txt or self.cfg.old.txt
        if not txt:
            return
        self.addbus()
        e = Command({"txt": txt, "orig": repr(self)})
        cmd(self, e)
        e.wait()

class Test(CLI):

    def dosay(self, channel, txt):
        if self.cfg.verbose:
            print(txt)

class Console(CLI):

    def poll(self):
        return input("> ")

    def post(self, e):
        e.wait()
