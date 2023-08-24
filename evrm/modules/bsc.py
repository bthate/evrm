# This file is placed in the Public Domain.
#
# pylint: disable=C0116,E0402


"basic commands"


from ..reactor import Client


def __dir__():
    return (
            "cmd",
           )


def cmd(event):
    event.reply(",".join(sorted(Client.cmds)))
