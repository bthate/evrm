# This file is placed in the Public Domain.
#
# pylint: disable=C0115,C0116,W0105,E0402,R0903


"shopping list"


import time


from ..objects import Object
from ..storage import find, fntime, write
from ..threads import laps


def __dir__():
    return (
            "got",
            "sop"
           )


class Shop(Object):

    def __init__(self):
        super().__init__()
        self.txt = ''


def got(event):
    if not event.args:
        event.reply("got <txt>")
        return
    selector = {'txt': event.args[0]}
    nrs = 0
    for obj in find('shop', selector):
        nrs += 1
        obj.__deleted__ = True
        write(obj)
        event.reply('ok')
    if not nrs:
        event.reply("no shops")


def shp(event):
    if not event.rest:
        nmr = 0
        for obj in find('shop'):
            lap = laps(time.time()-fntime(obj.__oid__))
            event.reply(f'{nmr} {obj.txt} {lap}')
            nmr += 1
        if not nmr:
            event.reply("no shops")
        return
    obj = Shop()
    obj.txt = event.rest
    write(obj)
    event.reply('ok')
