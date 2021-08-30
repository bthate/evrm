# This file is placed in the Public Domain.

from .obj import Object, update


class ENoTxt(Exception):

    pass

class Token(Object):

    pass


class Word(Token):

    def __init__(self, txt=None):
        super().__init__()
        if txt is None:
            txt = ""
        self.txt = txt


class Option(Token):

    def __init__(self, txt):
        super().__init__()
        if txt.startswith("--"):
            self.opt = txt[2:]
        elif txt.startswith("-"):
            self.opt = txt[1:]


class Getter(Token):

    def __init__(self, txt):
        super().__init__()
        if "==" in txt:
            pre, post = txt.split("==", 1)
        else:
            pre = post = ""
        if pre:
            self[pre] = post


class Setter(Token):

    def __init__(self, txt):
        super().__init__()
        if "=" in txt:
            pre, post = txt.split("=", 1)
        else:
            pre = post = ""
        if pre:
            self[pre] = post


class Skip(Token):

    def __init__(self, txt):
        super().__init__()
        pre = ""
        if txt.endswith("-"):
            if "=" in txt:
                pre, _post = txt.split("=", 1)
            elif "==" in txt:
                pre, _post = txt.split("==", 1)
            else:
                pre = txt
        if pre:
            self[pre] = True


class Url(Token):

    def __init__(self, txt):
        super().__init__()
        self.url = ""
        if txt.startswith("http"):
            self.url = txt


def parse_txt(o, ptxt=None):
    if ptxt is None:
        raise ENoTxt(o)
    o.txt = ptxt
    o.otxt = ptxt
    o.gets = Object()
    o.opts = Object()
    o.timed = []
    o.index = None
    o.sets = Object()
    o.skip = Object()
    args = []
    for t in [Word(txt) for txt in ptxt.rsplit()]:
        u = Url(t.txt)
        if u and "url" in u and u.url:
            args.append(u.url)
        s = Skip(t.txt)
        if s:
            update(o.skip, s)
            t.txt = t.txt[:-1]
        s = Setter(t.txt)
        if s:
            update(o.sets, s)
            continue
        g = Getter(t.txt)
        if g:
            update(o.gets, g)
            continue
        opt = Option(t.txt)
        if opt:
            try:
                o.index = int(opt.opt)
                continue
            except ValueError:
                pass
            if len(opt.opt) > 1:
                for op in opt.opt:
                    o.opts[op] = True
            else:
                o.opts[opt.opt] = True
            continue
        args.append(t.txt)
    if not args:
        o.args = []
        o.cmd = ""
        o.rest = ""
        o.txt = ""
        return o
    o.cmd = args[0]
    o.args = args[1:]
    o.txt = " ".join(args)
    o.rest = " ".join(args[1:])
    return o


def parse_ymd(daystr):
    valstr = ""
    val = 0
    total = 0
    for c in daystr:
        if c in "1234567890":
            vv = int(valstr)
        else:
            vv = 0
        if c == "y":
            val = vv * 3600 * 24 * 365
        if c == "w":
            val = vv * 3600 * 24 * 7
        elif c == "d":
            val = vv * 3600 * 24
        elif c == "h":
            val = vv * 3600
        elif c == "m":
            val = vv * 60
        else:
            valstr += c
        total += val
    return total
