# This file is in the Public Domain.

"commands"

from .bus import Bus

def cmd(event):
    b = event.bot()
    event.reply(",".join(sorted(b.modnames)))

def ech(event):
    if event.rest:
        event.reply(event.rest)
