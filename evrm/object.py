# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R,W0622,W0108
# flake8: noqa=C901


"a clean namespace"


import datetime
import os
import uuid
import _thread


def __dir__():
    return (
            "Object",
            'clear',
            'copy',
            'edit',
            'fromkeys',
            'get',
            'ident',
            'items',
            'keys',
            'kind',
            'pop',
            'popitem',
            'printable',
            'search',
            'setdefault',
            'update',
            'values',
           )


__all__ = __dir__()



disklock = _thread.allocate_lock()


class Object:

    __slots__ = ("__dict__", "__oid__")

    def __init__(self, *args, **kwargs):
        self.__oid__ = ident(self)
        if args:
            val = args[0]
            if isinstance(val, list):
                update(self, dict(val))
            elif isinstance(val, zip):
                update(self, dict(val))
            elif isinstance(val, dict):
                update(self, val)
            elif isinstance(val, Object):
                update(self, vars(val))
        if kwargs:
            update(self, kwargs)

    def __contains__(self, key):
        return key in self.__dict__

    def __delitem__(self, key):
        return self.__dict__.__delitem__(key)

    def __getitem__(self, key):
        return self.__dict__.__getitem__(key)

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __setitem__(self, key, value):
        return self.__dict__.__setitem__(key, value)

    def __str__(self):
        res = "{"
        for key, value in items(self):
            if issubclass(type(value), Object):
                cur = str(value)
                res += f"'{key}': {cur}, "
            else:
                res += f"'{key}': '{value}', "
        if len(res) > 2:
            res = res[:-2]
        res += "}"
        return res


class Default(Object):

    __slots__ = ("__default__",)

    def __init__(self, *args, **kwargs):
        Object.__init__(self, *args, **kwargs)
        self.__default__ = ""

    def __getattr__(self, key):
        if key in self:
            return self[key]
        return self.__default__


def clear(self):
    self.__dict__ = {}


def copy(self, obj2):
    self.__dict__.update(obj2.__dict__)


def edit(self, setter, skip=False):
    try:
        setter = vars(setter)
    except (TypeError, ValueError):
        pass
    if not setter:
        setter = {}
    count = 0
    for key, val in setter.items():
        if skip and val == "":
            continue
        count += 1
        try:
            setattr(self, key, int(val))
            continue
        except ValueError:
            pass
        try:
            setattr(self, key, float(val))
            continue
        except ValueError:
            pass
        if val in ["True", "true"]:
            setattr(self, key, True)
        elif val in ["False", "false"]:
            setattr(self, key, False)
        else:
            setattr(self, key, val)
    return count


def fromkeys(self, keyz, value):
    for key in keyz:
        self[key] = value


def get(self, key, default=None):
    return getattr(self, key, default)


def ident(self) -> str:
    return os.path.join(
                        kind(self),
                        str(uuid.uuid4().hex),
                        os.sep.join(str(datetime.datetime.now()).split())
                       )

def items(self) -> []:
    if isinstance(self, type({})):
        return self.items()
    return self.__dict__.items()


def keys(self) -> []:
    return self.__dict__.keys()


def kind(self) -> str:
    kin = str(type(self)).split()[-1][1:-2]
    if kin == "type":
        kin = self.__name__
    return kin


def pop(self, key, default=None):
    if key in self:
        val = self[key]
        del self[key]
        return val
    if default:
        return default
    raise KeyError(key)


def popitem(self):
    if not self:
        raise KeyError
    for key, value in items(self):
        yield key, value


def printable(self, args="", skip="", plain=False):
    res = []
    keyz = []
    if "," in args:
        keyz = args.split(",")
    if not keyz:
        keyz = keys(self)
    for key in sorted(keyz):
        if key.startswith("_"):
            continue
        if skip:
            skips = skip.split(",")
            if key in skips:
                continue
        value = getattr(self, key, None)
        if not value:
            continue
        if " object at " in str(value):
            continue
        txt = ""
        if plain:
            value = str(value)
            txt = f'{value}'
        elif isinstance(value, str) and len(value.split()) >= 2:
            txt = f'{key}="{value}"'
        else:
            txt = f'{key}={value}'
        res.append(txt)
    txt = " ".join(res)
    return txt.strip()


def search(self, selector) -> bool:
    res = False
    for key, value in items(selector):
        try:
            val = self[key]
            if str(value) in str(val):
                res = True
                break
        except KeyError:
            continue
    return res


def setdefault(self, key, default):
    if key not in self:
        self[key] = default
    return self[key]


def update(self, data, empty=True) -> None:
    for key, value in items(data):
        if empty and not value:
            continue
        self[key] = value


def values(self) -> []:
    return self.__dict__.values()
