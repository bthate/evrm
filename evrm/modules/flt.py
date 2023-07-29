# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R,W0401,W0622
# flake8: noqa


"list of bots"


from ..bus    import Bus
from ..object import printable


def __dir__():
    return (
            'flt',
           )


__all__ = __dir__()


def flt(event):
    try:
        index = int(event.args[0])
        event.reply(printable(Bus.objs[index]))
        return
    except (KeyError, TypeError, IndexError, ValueError):
        pass
    event.reply(' | '.join([repr(obj).split()[0].split(".")[-1] for obj in Bus.objs]))
