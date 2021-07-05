# This is file is placed in Public Domain.

from ob import kernel

def __dir__():
    return ("cmd",)

def cmd(event):
    k = kernel()
    event.reply(",".join(sorted(k.cmds)))
