# This file is placed in the Public Domain.

import inspect
import pkgutil
import sys

from .obj import List, Object, spl

class Table(Object):

    def __init__(self):
        super().__init__()
        self.classes = Object()
        self.modnames = Object()
        self.names = List()

    def add(self, func):
        n = func.__name__
        self.modnames[n] = func.__module__

    def addcls(self, cls):
        self.classes[cls.__name__] = cls
        self.names.append(
            cls.__name__.lower(), "%s.%s" % (cls.__module__, cls.__name__)
        )

    def introspect(self, mod):
        for _k, o in inspect.getmembers(mod, inspect.isfunction):
            if o.__code__.co_argcount == 1 and "event" in o.__code__.co_varnames:
                self.add(o)
        for _k, o in inspect.getmembers(mod, inspect.isclass):
            if issubclass(o, Object):
                self.addcls(o)

    def scan(self, pkgs=""):
        for pn in spl(pkgs):
            p = sys.modules.get(pn, None)
            if not p:
                continue
            if "__path__" not in dir(p):
                self.introspect(p)
                continue
            for mn in pkgutil.walk_packages(p.__path__, pn + "."):
                mod = sys.modules.get(mn[1], None)
                if mod:
                    self.introspect(mod)
