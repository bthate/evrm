# This file is in the Public Domain.

"todo"

from op.dbs import find
from op.obj import Object, save

class Todo(Object):

    def __init__(self):
        super().__init__()
        self.txt = ""

def dne(event):
    if not event.args:
        event.reply("dne <stringintodo>")
        return
    selector = {"txt": event.args[0]}
    for fn, o in find("op.tdo.Todo", selector):
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
