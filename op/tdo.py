# This file is in the Public Domain.

"todo"

from botl.dbs import find
from botl.obj import Object, save

class Todo(Object):

    def __init__(self):
        super().__init__()
        self.txt = ""

def dne(event):
    if not event.args:
        event.reply("dne <stringintodo>")
        return
    selector = {"txt": event.args[0]}
    for fn, o in find("botd.tdo.Todo", selector):
        o._deleted = True
        save(o)
        event.reply("ok")
        break

def tdo(event):
    if not event.rest:
        event.reply("tdo <txt>")
        return
    o = Todo()
    o.txt = event.rest
    save(o)
    event.reply("ok")
