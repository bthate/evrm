# This file is placed in the Public Domain.

"objects"

import datetime
import importlib
import json as js
import os
import time
import types
import uuid
import _thread

from botl.err import ENOCLASS, ENOFILENAME

starttime = time.time()
wd = ""

class O:

    __slots__ = ("__dict__", "__stp__")

    def __init__(self, val=None):
        self.__stp__ = os.path.join(gettype(self), str(uuid.uuid4()), os.sep.join(str(datetime.datetime.now()).split()))
        if val:
            self.__dict__.update(val)

    def __delitem__(self, k):
        try:
            del self.__dict__[k]
        except KeyError:
            pass

    def __getitem__(self, k):
        return self.__dict__[k]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __lt__(self, o):
        return len(self) < len(o)

    def __setitem__(self, k, v):
        self.__dict__[k] = v

    def __str__(self):
        return js.dumps(self.__dict__, default=default, sort_keys=True)

class Object(O):

    def get(self, k, d=None):
        return self.__dict__.get(k, d)

    def keys(self):
        return self.__dict__.keys()

    def items(self):
        return self.__dict__.items()

    def register(self, k, v):
        self[str(k)] = v

    def update(self, d):
        return self.__dict__.update(d)

    def values(self):
        return self.__dict__.values()

class ObjectList(Object):

    def append(self, key, value):
        if key not in self:
            self[key] = []
        if value in self[key]:
            return
        if isinstance(value, list):
            self[key].extend(value)
        else:
            self[key].append(value)

    def update(self, d):
        for k, v in d.items():
            self.append(k, v)

class Default(Object):

    default = ""

    def __getattr__(self, k):
        try:
            return super().__getattribute__(k)
        except AttributeError:
            try:
                return super().__getitem__(k)
            except KeyError:
                return self.default

class Cfg(Default):

    pass

def cdir(path):
    if os.path.exists(path):
        return
    res = ""
    path2, _fn = os.path.split(path)
    for p in path2.split(os.sep):
        res += "%s%s" % (p, os.sep)
        padje = os.path.abspath(os.path.normpath(res))
        try:
            os.mkdir(padje)
            os.chmod(padje, 0o700)
        except (IsADirectoryError, NotADirectoryError, FileExistsError):
            pass

def dorepr(o):
    return '<%s.%s>' % (
        o.__class__.__module__,
        o.__class__.__name__,
    )

def getcls(fullname):
    try:
        modname, clsname = fullname.rsplit(".", 1)
    except Exception as ex:
        raise ENOCLASS(fullname) from ex
    mod = importlib.import_module(modname)
    return getattr(mod, clsname)

def hook(hfn):
    if hfn.count(os.sep) > 3:
        oname = hfn.split(os.sep)[-4:]
    else:
        oname = hfn.split(os.sep)
    cname = oname[0]
    fn = os.sep.join(oname)
    o = getcls(cname)()
    load(o, fn)
    return o

def default(o):
    if isinstance(o, O):
        return vars(o)
    if isinstance(o, dict):
        return o.items()
    if isinstance(o, list):
        return iter(o)
    if isinstance(o, (type(str), type(True), type(False), type(int), type(float))):
        return o
    return repr(o)

def fmt(o, keys=None, empty=True, skip=None):
    if keys is None:
        keys = o.keys()
    if not keys:
        keys = ["txt"]
    if skip is None:
        skip = []
    res = []
    txt = ""
    for key in sorted(keys):
        if key in skip:
            continue
        try:
            val = o[key]
        except KeyError:
            continue
        if empty and not val:
            continue
        val = str(val).strip()
        res.append((key, val))
    result = []
    for k, v in res:
        result.append("%s=%s%s" % (k, v, " "))
    txt += " ".join([x.strip() for x in result])
    return txt.strip()

def getname(o):
    t = type(o)
    if t == types.ModuleType:
        return o.__name__
    try:
        n = "%s.%s" % (o.__self__.__class__.__name__, o.__name__)
    except AttributeError:
        try:
            n = "%s.%s" % (o.__class__.__name__, o.__name__)
        except AttributeError:
            try:
                n = o.__class__.__name__
            except AttributeError:
                n = o.__name__
    return n

def gettype(o):
    return str(type(o)).split()[-1][1:-2]

def load(o, opath):
    assert wd
    if opath.count(os.sep) != 3:
        raise ENOFILENAME(opath)
    spl = opath.split(os.sep)
    stp = os.sep.join(spl[-4:])
    lpath = os.path.join(wd, "store", stp)
    with open(lpath, "r") as ofile:
        try:
            o.update(js.load(ofile, object_hook=Object))
        except js.decoder.JSONDecodeError as ex:
            return
    o.__stp__ = stp
    return stp

def save(o):
    assert wd
    prv = os.sep.join(o.__stp__.split(os.sep)[:2])
    o.__stp__ = os.path.join(prv, os.sep.join(str(datetime.datetime.now()).split()))
    opath = os.path.join(wd, "store", o.__stp__)
    cdir(opath)
    with open(opath, "w") as ofile:
        js.dump(o, ofile, default=default)
    os.chmod(opath, 0o444)
    return o.__stp__

def tojson(o):
    return js.dumps(o.__dict__, default=default, indent=4, sort_keys=True)
