# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R
# flake8: noqa


"todo list"

import time


from ..object  import Object
from ..persist import Persist, find, fntime, write
from ..utils   import laps


class Todo(Object):

    def __init__(self):
        Object.__init__(self)
        self.txt = ''


Persist.add(Todo)


def dne(event):
    if not event.args:
        event.reply("dne <txt>")
        return
    selector = {'txt': event.args[0]}
    nrs = 0
    for obj in find('todo', selector):
        nrs += 1
        obj.__deleted__ = True
        write(obj)
        event.reply('ok')
        break
    if not nrs:
        event.reply("nothing todo")


def tdo(event):
    if not event.rest:
        nmr = 0
        for obj in find('todo'):
            lap = laps(time.time()-fntime(obj.__oid__))
            event.reply(f'{nmr} {obj.txt} {lap}')
            nmr += 1
        if not nmr:
            event.reply("no todo")
        return
    obj = Todo()
    obj.txt = event.rest
    write(obj)
    event.reply('ok')
