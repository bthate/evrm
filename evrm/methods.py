# This file is placed in the Public Domain.
#
# pylint: disable=C0112,C0115,C0116,W0105,R0903,E0402


"methods"


def __dir__():
    return (
            'clear',
            'copy',
            'edit',
            'fromkeys',
            'get',
            'keys',
            'items',
            'prt',
            'pop',
            'popitem',
            'search',
            'setdefault',
            'update',
            'values'
           )


__all__ = __dir__()


"utility"


def doskip(txt, skipping) -> bool:
    for skp in spl(skipping):
        if skp in txt:
            return True
    return False


def spl(txt) -> []:
    try:
        res = txt.split(',')
    except (TypeError, ValueError):
        res = txt
    return [x for x in res if x]


"dict"


def clear(obj):
    obj.__dict__ = {}


def copy(obj, obj2):
    obj.__dict__.update(obj2.__dict__)


def fromkeys(obj, keyz, value):
    for key in keyz:
        obj[key] = value


def get(obj, key, default=None):
    return getattr(obj, key, default)


def items(obj) -> []:
    if isinstance(obj, type({})):
        return obj.items()
    return obj.__dict__.items()


def keys(obj) -> []:
    return obj.__dict__.keys()


def pop(obj, key, default=None):
    if key in obj:
        val = obj[key]
        del obj[key]
        return val
    if default:
        return default
    raise KeyError(key)


def popitem(obj):
    if not obj:
        raise KeyError
    for key, value in items(obj):
        yield key, value


def setdefault(obj, key, default):
    if key not in obj:
        obj[key] = default
    return obj[key]


def update(obj, data, empty=True) -> None:
    for key, value in items(data):
        if empty and not value:
            continue
        obj[key] = value


def values(obj) -> []:
    return obj.__dict__.values()


"other"


def edit(obj, setter, skip=False):
    try:
        setter = vars(setter)
    except (TypeError, ValueError):
        pass
    if not setter:
        setter = {}
    for key, val in setter.items():
        if skip and val == "":
            continue
        try:
            setattr(obj, key, int(val))
            continue
        except ValueError:
            pass
        try:
            setattr(obj, key, float(val))
            continue
        except ValueError:
            pass
        if val in ["True", "true"]:
            setattr(obj, key, True)
        elif val in ["False", "false"]:
            setattr(obj, key, False)
        else:
            setattr(obj, key, val)


def parse(obj, txt=None) -> None:
    args = []
    obj.args = []
    obj.cmd = obj.cmd or ""
    obj.gets = obj.gets or {}
    obj.hasmods = False
    obj.mod = obj.mod or ""
    obj.opts = obj.opts or ""
    obj.sets = obj.sets or {}
    obj.otxt = txt or ""
    _nr = -1
    for spli in obj.otxt.split():
        if spli.startswith("-"):
            try:
                obj.index = int(spli[1:])
            except ValueError:
                obj.opts += spli[1:]
            continue
        if "=" in spli:
            key, value = spli.split("=", maxsplit=1)
            if key == "mod":
                obj.hasmods = True
                if obj.mod:
                    obj.mod += f",{value}"
                else:
                    obj.mod = value
                continue
            obj.sets[key] = value
            continue
        if "==" in spli:
            key, value = spli.split("==", maxsplit=1)
            obj.gets[key] = value
            continue
        _nr += 1
        if _nr == 0:
            obj.cmd = spli
            continue
        args.append(spli)
    if args:
        obj.args = args
        obj.txt = obj.cmd or ""
        obj.rest = " ".join(obj.args)
        obj.txt = obj.cmd + " " + obj.rest
    else:
        obj.txt = obj.cmd


def prt(obj, args="", skip="", plain=False):
    res = []
    keyz = []
    if "," in args:
        keyz = args.split(",")
    if not keyz:
        keyz = obj.__dict__.keys()
    for key in sorted(keyz):
        if key.startswith("_"):
            continue
        if skip and doskip(key, skip):
            continue
        value = getattr(obj, key, None)
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


def search(obj, selector) -> bool:
    res = False
    for key, value in items(selector):
        try:
            val = obj[key]
            if str(value) in str(val):
                res = True
                break
        except KeyError:
            continue
    return res
