# This file is placed in the Public Domain.
#
# pylint: disable=C0112,C0115,C0116,W0105,R0902,R0903,E0402


"a clean namespace"


import datetime
import json
import os
import types
import uuid
import _thread


from json import JSONDecoder, JSONEncoder


hooklock = _thread.allocate_lock()
jsonlock = _thread.allocate_lock()


def __dir__():
    return (
            'Default',
            'Object',
           )


__all__ = __dir__()


class Object:

    __slots__ = ("__dict__", "__oid__")

    def __init__(self):
        self.__oid__ = ident(self)

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
        return str(self.__dict__)


class Default(Object):

    __default__ = ""

    def __getattr__(self, key):
        if key in self:
            return self[key]
        return Default.__default__


"utility"


def cls(obj):
    return kind(obj).split(".")[-1]


def construct(obj, *args, **kwargs):
    if args:
        val = args[0]
        if isinstance(val, list):
            update(obj, dict(val))
        elif isinstance(val, zip):
            update(obj, dict(val))
        elif isinstance(val, dict):
            update(obj, val)
        elif isinstance(val, Object):
            update(obj, vars(val))
    if kwargs:
        update(obj, kwargs)



def ident(obj) -> str:
    return os.path.join(
                        kind(obj),
                        str(uuid.uuid4().hex),
                        os.path.join(*str(datetime.datetime.now()).split())
                       )


def items(obj) -> []:
    if isinstance(obj, type({})):
        return obj.items()
    return obj.__dict__.items()


def kind(obj) -> str:
    kin = str(type(obj)).split()[-1][1:-2]
    if kin == "type":
        kin = obj.__name__
    return kin


def name(obj) -> str:
    typ = type(obj)
    if isinstance(typ, types.ModuleType):
        return obj.__name__
    if '__self__' in dir(obj):
        return f'{obj.__self__.__class__.__name__}.{obj.__name__}'
    if '__class__' in dir(obj) and '__name__' in dir(obj):
        return f'{obj.__class__.__name__}.{obj.__name__}'
    if '__class__' in dir(obj):
        return f"{obj.__class__.__module__}.{obj.__class__.__name__}"
    if '__name__' in dir(obj):
        return f'{obj.__class__.__name__}.{obj.__name__}'
    return None


def update(obj, data, empty=True) -> None:
    for key, value in items(data):
        if empty and not value:
            continue
        obj[key] = value


"decoder"


class ObjectDecoder(JSONDecoder):

    def __init__(self, *args, **kwargs):
        ""
        JSONDecoder.__init__(self, *args, **kwargs)

    def decode(self, s, _w=None):
        ""
        with jsonlock:
            val = JSONDecoder.decode(self, s)
            if not val:
                val = {}
            return hook(val)

    def raw_decode(self, s, idx=0):
        ""
        return JSONDecoder.raw_decode(self, s, idx)


def hook(objdict) -> type:
    with hooklock:
        obj = Object()
        construct(obj, objdict)
        return obj


def load(fpt, *args, **kw):
    kw["cls"] = ObjectDecoder
    kw["object_hook"] = hook
    return json.load(fpt, *args, **kw)


def loads(string, *args, **kw):
    kw["cls"] = ObjectDecoder
    kw["object_hook"] = hook
    return json.loads(string, *args, **kw)


"encoder"


class ObjectEncoder(JSONEncoder):

    def __init__(self, *args, **kwargs):
        ""
        JSONEncoder.__init__(self, *args, **kwargs)

    def default(self, o) -> str:
        ""
        if isinstance(o, dict):
            return o.items()
        if isinstance(o, Object):
            return vars(o)
        if isinstance(o, list):
            return iter(o)
        if isinstance(
                      o,
                      (
                       type(str),
                       type(True),
                       type(False),
                       type(int),
                       type(float)
                      )
                     ):
            return o
        try:
            return JSONEncoder.default(self, o)
        except TypeError:
            return object.__repr__(o)

    def encode(self, o) -> str:
        ""
        return JSONEncoder.encode(self, o)

    def iterencode(
                   self,
                   o,
                   _one_shot=False
                  ) -> str:
        ""
        return JSONEncoder.iterencode(self, o, _one_shot)


def dump(*args, **kw) -> None:
    kw["cls"] = ObjectEncoder
    return json.dump(*args, **kw)


def dumps(*args, **kw) -> str:
    kw["cls"] = ObjectEncoder
    return json.dumps(*args, **kw)
