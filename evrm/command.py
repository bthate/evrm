# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R,W0718
# flake8: noqa


"commands"


import inspect
import os


from .bus    import Bus
from .error  import Error
from .thread import launch
from .utils  import spl


class Command:

    cmds = {}
    errors = []

    @staticmethod
    def add(func):
        Command.cmds[func.__name__] = func

    @staticmethod
    def handle(evt):
        if "txt" in dir(evt):
            evt.parse(evt.txt)
            func = Command.cmds.get(evt.cmd, None)
            if func:
                try:
                    func(evt)
                    Bus.show(evt)
                except Exception as ex:
                    exc = ex.with_traceback(ex.__traceback__)
                    Error.errors.append(exc)
        evt.ready()

    @staticmethod
    def remove(name):
        try:
            del Command.cmds[name]
        except KeyError:
            pass

    @staticmethod
    def scan(mod) -> None:
        for key, cmd in inspect.getmembers(mod, inspect.isfunction):
            if key.startswith("cb"):
                continue
            if 'event' in cmd.__code__.co_varnames:
                Command.add(cmd)


def scan(pkg, mods, init=None, doall=False, wait=False) -> None:
    if not pkg:
        return
    path = pkg.__path__[0]
    if doall:
        modlist = [
                   x[:-3] for x in os.listdir(path)
                   if x.endswith(".py")
                   and x not in ["__init__.py", "__main__.py"]
                  ]
        mods = ",".join(sorted(modlist))
    threads = []
    for modname in spl(mods):
        module = getattr(pkg, modname, None)
        if not module:
            continue
        Command.scan(module)
        if init and "start" in dir(module):
            threads.append(launch(module.start, name=modname))
    if wait and threads:
        for thr in threads:
            thr.join()
