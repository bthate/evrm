# This file is in the Public Domain.

import ob

def __dir__():
    return ("Todo", "dne", "tdo")

class Todo(ob.Object):

    def __init__(self):
        super().__init__()
        self.txt = ""

def dne(clt, event):
    if not event.args:
        event.reply("dne txt==<string>")
        return
    db = ob.Db()
    for fn, o in db.find("om.tdo.Todo", event.gets):
        o._deleted = True
        o.save()
        event.reply("ok")
        break

def tdo(event):
    if not event.rest:
        event.reply("tdo <txt>")
        return
    o = Todo()
    o.txt = event.rest
    o.save()
    event.reply("ok")
