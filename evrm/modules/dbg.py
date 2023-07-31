# This file is placed in the Public Domain.


"debug"


from ..run import Cfg


def dbg(event):
    if Cfg.error:
        event.reply("raising")
        raise Exception("debug")
    else:
        event.reply("error is not enabled")