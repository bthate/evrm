# This file is placed in the Public Domain.

from .bus import Bus
from .obj import Default, Object, ObjectList
from .itr import findcmds, hasmod
from .itr import scan as iscan
from .utl import direct, spl
from .zzz import os, sys

class Loader(Object):

    cmds = Object()
    modnames = Object()
    names = ObjectList()
    pnames = Object()
    table = Object()
    tbl = Object()

    def add(self, name, cmd):
        self.cmds.register(name, cmd)
        self.modnames[name] = cmd.__module__

    def addbus(self):
        Bus.add(self)

    def cmd(self, cmd):
        if cmd not in self.cmds:
            mn = self.modname(cmd)
            if mn:
                self.load(mn)
        return self.cmds.get(cmd, None)

    def init(self, mns):
        for mn in spl(mns):
            mnn = self.name(mn)
            if mnn and hasmod(mnn):
                mod = self.load(mnn)
                if mod and "init" in dir(mod):
                    mod.init(self)

    def loader(self, mnn):
        if mnn in Loader.table:
            return self.table[mnn]
        Loader.table[mnn] = direct(mnn)
        return Loader.table[mnn]

    def load(self, mn):
        mod = self.loader(mn)
        cmds = findcmds(mod)
        self.cmds.update(cmds)
        return mod

    def name(self, mn):
        return Loader.pnames.get(mn, None)

    def modname(self, mn):
        return Loader.modnames.get(mn, None)

    def scan(self, path, name=""):
        if not os.path.exists(path):
            return
        if not name:
            name = path.split(os.sep)[-1]
        r = os.path.dirname(path)
        sys.path.insert(0, r)
        for mn in [x[:-3] for x in os.listdir(path)
                   if x and x.endswith(".py")
                   and not x.startswith("__")
                   and not x == "setup.py"]:
            fqn = "%s.%s" % (name, mn)
            mod = self.load(fqn)
            iscan(self, mod)

    def tbl(self, tbl):
        Loader.names = ObjectList()
        Loader.names.update(tbl["names"])
        Loader.modnames.update(tbl["modnames"])
        Loader.pnames.update(tbl["pnames"])

    def types(self, typ):
        return list(Loader.names.get(typ, [typ,]))
