# This file is placed in the Public Domain.

import getpass
import os
import pwd
import sys
import time

from .bus import Bus
from .obj import Db, Default, Object, cdir, get, getmain, getwd, spl, update
from .hdl import Dispatcher, Handler, Loop
from .prs import parse_txt


starttime = time.time()


class Cfg(Default):


    def __init__(self):
        super().__init__()
        self.debug = False
        self.verbose = False


class Runtime(Dispatcher, Loop):

    def __init__(self):
        Dispatcher.__init__(self)
        Loop.__init__(self)
        self.cfg = Cfg()
        self.classes = Object()
        self.cmds = Object()
        self.opts = Object()
        self.register("cmd", self.handle)

    def boot(self, disk=False):
        self.parse_cli(disk)
        cdir(getwd()+os.sep)
        cdir(os.path.join(getwd(), "store", ""))

    def cmd(self, txt):
        if not txt:
            return None
        c = getmain("clt")
        if c:
            e = c.event(txt)
            e.origin = "root@shell"
            self.handle(c, e)
            e.wait()
        return None

    def do(self, e):
        self.dispatch(e)

    def error(self, txt):
        pass

    def handle(self, clt, obj):
        obj.parse()
        f = None
        t = getmain("tbl")
        if t:
            mn = get(t.modnames, obj.cmd, None)
            if mn:
                mod = sys.modules.get(mn, None)
                if mod:
                    f = getattr(mod, obj.cmd, None)
        if not f:
            f = get(self.cmds, obj.cmd, None)
        if f:
            f(obj)
            obj.show()
        obj.ready()

    def init(self, mns):
        k = getmain("k")
        mods = []
        for mn in spl(mns):
            mod = sys.modules.get(mn, None)
            if not mod:
                continue
            i = getattr(mod, "init", None)
            if i:
                k.log("init %s" % mn)
                i(self)
            mods.append(mod)
        return mods

    def opt(self, ops):
        if not self.opts:
            return False
        for opt in ops:
            if opt in self.opts:
                return True
        return False

    def parse_cli(self, disk=False):
        o = Default()
        if disk:
            db = Db()
            oo = db.lastobject(self.cfg)
            if oo:
                update(o, oo)
        txt = " ".join(sys.argv[1:])
        if txt:
            parse_txt(o, txt)
        update(self.cfg, o)
        if o.sets:
            update(self.cfg, o.sets)
        if o.opts:
            update(self.opts, o.opts)

    @staticmethod
    def privileges(name=None):
        if os.getuid() != 0:
            return None
        try:
            pwn = pwd.getpwnam(name)
        except (TypeError, KeyError):
            name = getpass.getuser()
            try:
                pwn = pwd.getpwnam(name)
            except (TypeError, KeyError):
                return None
        if name is None:
            try:
                name = getpass.getuser()
            except (TypeError, KeyError):
                pass
        try:
            pwn = pwd.getpwnam(name)
        except (TypeError, KeyError):
            return False
        try:
            os.chown(getwd(), pwn.pw_uid, pwn.pw_gid)
        except PermissionError:
            pass
        os.setgroups([])
        os.setgid(pwn.pw_gid)
        os.setuid(pwn.pw_uid)
        os.umask(0o22)
        return True

    @staticmethod
    def root():
        if os.geteuid() != 0:
            return False
        return True

    @staticmethod
    def wait():
        while 1:
            time.sleep(5.0)

class Client(Handler):

    def __init__(self):
        super().__init__()
        self.cfg = Cfg()
        Bus.add(self)

    def handle(self, clt, e):
        k = getmain("k")
        if k:
            k.put(e)

    def raw(self, txt):
        pass

    def say(self, channel, txt):
        self.raw(txt)
