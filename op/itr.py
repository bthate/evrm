# This file is placed in the Public Domain.

"introspection"

from .obj import Object, ObjectList
from .utl import direct, spl, hasmod
from .zzz import os, importlib, inspect, pkgutil, sys

def findall(pkgs):
    for pn in spl(pkgs):
        try:
            mod = direct(pn)
        except ModuleNotFoundError:
            continue
        if "__file__" in dir(mod) and mod.__file__:
            pths = [os.path.dirname(mod.__file__),]
            for m, n, p in pkgutil.iter_modules(pths):
                fqn = "%s.%s" % (pn, n)
                yield fqn
        else:
            p = list(mod.__path__)[0]
            if not os.path.exists(p):
                continue
            for mn in [x[:-3] for x in os.listdir(p) if x.endswith(".py")]:
                fqn = "%s.%s" % (pn, mn)
                yield fqn

def findcmds(mod):
    cmds = Object()
    for key, o in inspect.getmembers(mod, inspect.isfunction):
        if "event" in o.__code__.co_varnames:
            if o.__code__.co_argcount == 1:
                if key not in cmds:
                    cmds[key] = o
    return cmds

def findclass(mod):
    mds = ObjectList()
    for key, o in inspect.getmembers(mod, inspect.isclass):
        if issubclass(o, Object):
            mds.append(o.__name__, o.__module__)
    return mds

def findclasses(mod):
    nms = ObjectList()
    for _key, o in inspect.getmembers(mod, inspect.isclass):
        if issubclass(o, Object):
            t = "%s.%s" % (o.__module__, o.__name__)
            nms.append(o.__name__, t)
    return nms

def findfuncs(mod):
    funcs = Object()
    for key, o in inspect.getmembers(mod, inspect.isfunction):
        if "event" in o.__code__.co_varnames:
            if o.__code__.co_argcount == 1:
                if key not in funcs:
                    funcs[key] = "%s.%s" % (o.__module__, o.__name__)
    return funcs

def findmods(mod):
    mods = Object()
    for key, o in inspect.getmembers(mod, inspect.isfunction):
        if "event" in o.__code__.co_varnames:
            if o.__code__.co_argcount == 1:
                if key not in mods:
                    mods[key] = o.__module__
    return mods

def findmodules(pns):
    mods = []
    for mn in findall(pns):
        if mn in mods:
            continue
        mod = direct(mn)
        mods.append(mod)
    return mods

def findnames(mod):
    tps = Object()
    for _key, o in inspect.getmembers(mod, inspect.isclass):
        if issubclass(o, Object):
            t = "%s.%s" % (o.__module__, o.__name__)
            if t not in tps:
                tps[o.__name__.lower()] = t
    return tps


def getargs(f):
    spec = inspect.signature(f)
    return spec.parameters

def getnames(pkgs):
    res = Object()
    for pkg in spl(pkgs):
        for mod in getmods(pkg):
            n = findnames(mod)
            res.update(n)
    return res

def getmods(mn):
    mod = []
    for name in spl(mn):
        try:
            pkg = direct(name)
        except ModuleNotFoundError:
            continue
        path = list(pkg.__path__)[0]
        for m in ["%s.%s" % (name, x.split(os.sep)[-1][:-3]) for x in os.listdir(path)
                  if x.endswith(".py")
                  and not x == "setup.py"]:
            try:
                mod.append(direct(m))
            except ModuleNotFoundError:
                continue
    return mod

def hasmod(fqn):
    if fqn in sys.modules:
        return True
    try:
        spec = importlib.util.find_spec(fqn)
        if spec:
            return True
    except (ValueError, ModuleNotFoundError):
        pass
    try:
        direct(fqn)
        return True
    except ModuleNotFoundError:
        pass
    return False    

def scan(h, mod):
    mn = mod.__name__
    h.pnames[mn.split(".")[-1]] = mn
    h.modnames.update(findmods(mod))
    h.names.update(findnames(mod))

def scandir(h, path, name=""):
    if not os.path.exists(path):
        return
    if not name:
        name = path.split(os.sep)[-1]
    r = os.path.dirname(path)
    if r not in sys.path:
        sys.path.insert(0, r)
    for mn in [x[:-3] for x in os.listdir(path)
               if x and x.endswith(".py")
               and not x.startswith("__")
               and not x == "setup.py"]:
        fqn = "%s.%s" % (name, mn)
        if not hasmod(fqn):
            continue
        mod = h.load(fqn)
        scan(h, mod)

def walk(names):
    o = {}
    o["pnames"] = {}
    o["names"] = {}
    o["modnames"] = {}
    for mn in findall(names):
        mod = direct(mn)
        if "cmd" not in mn:
            o["pnames"][mn.split(".")[-1]] = mn
        o["modnames"].update(findmods(mod))
        for k, v in findnames(mod).items():
            if k not in o["names"]:
                o["names"][k] = []
            if v not in o["names"][k]:
                o["names"][k].append(v)
    return o
