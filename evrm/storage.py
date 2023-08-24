# This file is placed in the Public Domain.
#
# pylint: disable=C0112,C0115,C0116,W0105,R0903,E0402,C0209


"persistence"


import inspect
import os
import pathlib
import sys
import time
import _thread


from .objects import Object, ident, kind, load, dump
from .methods import keys, search, update


def __dir__():
    return (
            'NoClass',
            'Storage',
            'last',
            'read',
            'write'
           )


__all__ = __dir__()


disklock = _thread.allocate_lock()


class NoClass(Exception):

    pass


class Storage:

    classes = Object()
    workdir = os.path.expanduser('~/.%s' % __file__.split(os.sep)[-2])

    @staticmethod
    def add(clz):
        if not clz:
            return
        name = str(clz).split()[1][1:-2]
        Storage.classes[name] = clz

    @staticmethod
    def long(name):
        split = name.split(".")[-1].lower()
        res = None
        for named in keys(Storage.classes):
            if split in named.split(".")[-1].lower():
                res = named
                break
        return res

    @staticmethod
    def path(pth):
        return os.path.join(Storage.store(), pth)

    @staticmethod
    def scan(mod) -> None:
        for key, clz in inspect.getmembers(mod, inspect.isclass):
            if key.startswith("cb"):
                continue
            if not issubclass(clz, Object):
                continue
            Storage.add(clz)

    @staticmethod
    def store(pth=""):
        return os.path.join(Storage.workdir, "store", pth)


"utility"


def cdir(pth) -> None:
    if not pth.endswith(os.sep):
        pth = os.path.dirname(pth)
    pth = pathlib.Path(pth)
    os.makedirs(pth, exist_ok=True)


def files() -> []:
    return os.listdir(Storage.store())


def find(mtc, selector=None) -> []:
    if selector is None:
        selector = {}
    for fnm in reversed(sorted(fns(mtc), key=fntime)):
        clzname = fnclass(fnm)
        clz = sys.modules.get(clzname, None)
        if not clz:
            clz = Object
        obj = clz()
        read(obj, fnm)
        if '__deleted__' in obj:
            continue
        if selector and not search(obj, selector):
            continue
        yield obj


def fns(mtc) -> []:
    assert Storage.workdir
    dname = ''
    clz = Storage.long(mtc)
    if not clz:
        raise NoClass(mtc)
    path = Storage.path(clz)
    for rootdir, dirs, _files in os.walk(path, topdown=False):
        if dirs:
            dname = sorted(dirs)[-1]
            if dname.count('-') == 2:
                ddd = os.path.join(rootdir, dname)
                fls = sorted(os.listdir(ddd))
                if fls:
                    yield strip(os.path.join(ddd, fls[-1]))


def fnclass(fnm):
    return fnm.split(os.sep)[-4]


def fntime(daystr) -> float:
    daystr = daystr.replace('_', ':')
    datestr = ' '.join(daystr.split(os.sep)[-2:])
    if '.' in datestr:
        datestr, rest = datestr.rsplit('.', 1)
    else:
        rest = ''
    timed = time.mktime(time.strptime(datestr, '%Y-%m-%d %H:%M:%S'))
    if rest:
        timed += float('.' + rest)
    else:
        timed = 0
    return timed


def strip(path) -> str:
    return os.sep.join(path.split(os.sep)[-4:])


"methods"


def last(obj, selector=None) -> None:
    if selector is None:
        selector = {}
    result = sorted(
                    find(kind(obj), selector),
                    key=lambda x: fntime(x.__oid__)
                   )
    if result:
        inp = result[-1]
        update(obj, inp)
        obj.__oid__ = inp.__oid__
    return obj.__oid__


def read(obj, pth) -> str:
    with disklock:
        pth = os.path.join(Storage.store(), pth)
        with open(pth, 'r', encoding='utf-8') as ofile:
            data = load(ofile)
            update(obj, data)
        obj.__oid__ = strip(pth)
        return obj.__oid__


def write(obj) -> str:
    with disklock:
        try:
            pth = obj.__oid__
        except (AttributeError, TypeError):
            pth = ident(obj)
        pth = os.path.join(Storage.store(), pth)
        cdir(pth)
        with open(pth, 'w', encoding='utf-8') as ofile:
            dump(obj, ofile)
        return os.sep.join(pth.split(os.sep)[-4:])
