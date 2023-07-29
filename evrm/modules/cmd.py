# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R


"commands"


from ..command import Command


def __dir__():
    return (
            'cmd',
           )


__all__ = __dir__()


def cmd(event):
    event.reply(",".join(sorted(Command.cmds)))
