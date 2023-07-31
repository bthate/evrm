# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R,W0622,W0108
# flake8: noqa=C901


"persistence"


import os
import sys
import time


from .json   import dump, load
from .locks  import disklock, hooklock
from .object import Object, ident, keys, kind, search, update
from .utils  import cdir, strip


def __dir__():
    return (
            'Persist',
            'find',
            'fntime',
            'read',
            'write'
           ) 


__all__ = __dir__()


class Persist:

    classes = Object()
    workdir = f".{__file__.split(os.sep)[-2]}"

    @staticmethod
    def add(clz):
        if not clz:
            return
        name = str(clz).split()[1][1:-2]
        Persist.classes[name] = clz

    @staticmethod
    def long(nme):
        spl = nme.split(".")[-1].lower()
        for name in keys(Persist.classes):
            if spl in name.split(".")[-1].lower():
                return name

    @staticmethod
    def path(pth):
        return os.path.join(Persist.store(), pth)

    @staticmethod
    def store(pth=""):
        return os.path.join(Persist.workdir, "store", pth)


def files() -> []:
    return os.listdir(Persist.store())


def find(mtc, selector=None) -> []:
    if selector is None:
        selector = {}
    for fnm in reversed(sorted(fns(mtc), key=lambda x: fntime(x))):
        ppth = os.path.join(mtc, fnm)
        obj = hook(ppth)
        if '__deleted__' in obj:
            continue
        if selector and not search(obj, selector):
            continue
        yield obj


def fns(mtc) -> []:
    assert Persist.workdir
    dname = ''
    clz = Persist.long(mtc)
    #lst = mtc.lower().split(".")[-1]
    path = os.path.join(Persist.store(), clz)
    for rootdir, dirs, _files in os.walk(path, topdown=False):
        if dirs:
            dname = sorted(dirs)[-1]
            if dname.count('-') == 2:
                ddd = os.path.join(rootdir, dname)
                fls = sorted(os.listdir(ddd))
                if fls:
                    yield os.path.join(ddd, fls[-1])


def fntime(daystr) -> float:
    daystr = daystr.replace('_', ':')
    datestr = ' '.join(daystr.split(os.sep)[-2:])
    if '.' in datestr:
        datestr, rest = datestr.rsplit('.', 1)
    else:
        rest = ''
    tme = time.mktime(time.strptime(datestr, '%Y-%m-%d %H:%M:%S'))
    if rest:
        tme += float('.' + rest)
    else:
        tme = 0
    return tme


def hook(pth) -> type:
    with hooklock:
        clz = pth.split(os.sep)[-4]
        splitted = clz.split(".")
        modname = ".".join(splitted[:1])
        clz = splitted[-1]
        mod = sys.modules.get(modname, None)
        if mod:
            cls = getattr(mod, clz, None)
        if cls:
            obj = cls()
            read(obj, pth)
            return obj
        obj = Object()
        read(obj, pth)
        return obj


def last(self, selector=None) -> None:
    if selector is None:
        selector = {}
    result = sorted(
                    find(kind(self), selector),
                    key=lambda x: fntime(x.__oid__)
                   )
    if result:
        inp = result[-1]
        update(self, inp)
        self.__oid__ = inp.__oid__
    return self.__oid__


def read(self, pth) -> str:
    with disklock:
        pth = os.path.join(Persist.workdir, "store", pth)
        with open(pth, 'r', encoding='utf-8') as ofile:
            data = load(ofile)
            update(self, data)
        self.__oid__ = os.sep.join(pth.split(os.sep)[-4:])
        return self.__oid__


def write(self) -> str:
    with disklock:
        try:
            pth = self.__oid__
        except TypeError:
            pth = ident(self)
        pth = os.path.join(Persist.workdir, "store", pth)
        cdir(pth)
        with open(pth, 'w', encoding='utf-8') as ofile:
            dump(self, ofile)
        return os.sep.join(pth.split(os.sep)[-4:])
