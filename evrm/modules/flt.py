# This file is placed in the Public Domain.
#
# pylint: disable=C0116,E0402


"list of bots"


from ..reactor import Broker


def __dir__():
    return (
            "flt",
           )


def flt(event):
    try:
        index = int(event.args[0])
        event.reply(str(Broker.objs[index]))
        return
    except (KeyError, TypeError, IndexError, ValueError):
        pass
    event.reply(
                ' | '.join([repr(obj).split()[0].split(".")[-1]
                            for obj in Broker.objs])
               )
