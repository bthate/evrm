# This file is in the Public Domain.

"administrator"

from .bus import Bus
from .dbs import last
from .edt import edit
from .irc import __version__
from .obj import Object, fmt, getname, save, starttime
from .tms import elapsed
from .trc import exc as iexc
from .zzz import threading, time

def exc(event):
    if iexc:
        event.reply("|".join(iexc))

def flt(event):
    try:
        index = int(event.args[0])
        event.reply(str(Bus.objs[index]))
        return
    except (TypeError, IndexError):
        pass
    event.reply(" | ".join([getname(o) for o in Bus.objs]))

def krn(event):
    b = event.bot()
    if not event.sets:
        event.reply(fmt(b.cfg, skip=["opts", "sets", "old", "res"]))
        return
    edit(b.cfg, event.sets)
    save(b.cfg)
    event.reply("ok")

def sve(event):
    b = event.bot()
    save(b)
    event.reply("ok")

def thr(event):
    psformat = "%s %s"
    result = []
    for thr in sorted(threading.enumerate(), key=lambda x: x.getName()):
        if str(thr).startswith("<_"):
            continue
        o = Object()
        o.update(vars(thr))
        if o.get("sleep", None):
            up = o.sleep - int(time.time() - o.state.latest)
        else:
            up = int(time.time() - starttime)
        thrname = thr.getName()
        if not thrname:
            continue
        if thrname:
            result.append((up, thrname))
    res = []
    for up, txt in sorted(result, key=lambda x: x[0]):
        res.append("%s %s" % (txt, elapsed(up)))
    if res:
        event.reply(" | ".join(res))

def upt(event):
    event.reply("uptime is %s" % elapsed(time.time() - starttime))

def ver(event):
    b = event.bot()
    event.reply("%s %s" % (b.cfg.name.upper(), b.cfg.version or __version__))
