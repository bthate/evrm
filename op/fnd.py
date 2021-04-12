# This file is placed in the Public Domain.

"find"

from .dbs import find, listfiles
from .obj import fmt
from .tms import elapsed, fntime
from .zzz import time

import botl.obj

def fnd(event):
    if not event.args:
        fls = listfiles(botl.obj.wd)
        if fls:
            event.reply("|".join([x.split(".")[-1].lower() for x in fls]))
        return
    name = event.args[0]
    b = event.bot()
    t = b.types(name)
    nr = -1
    args = list(event.gets)
    try:
        args.extend(event.args[1:])
    except IndexError:
        pass
    for otype in t:
        for fn, o in find(otype, event.gets, event.index, event.timed):
            nr += 1
            txt = "%s %s" % (str(nr), fmt(o, args or o.keys()))
            if b.op("t") or "t" in event.opts:
                txt = txt + " %s" % (elapsed(time.time() - fntime(fn)))
            event.reply(txt)
