# This file is placed in the Public Domain.
#
# pylint: disable=C0116,W0719,E0402


"debug"


from ..reactor import Cfg


def __dir__():
    return (
            "dbg",
           )


def dbg(event):
    if Cfg.error:
        event.reply("raising")
        raise Exception("debug")
    event.reply("error is not enabled")
