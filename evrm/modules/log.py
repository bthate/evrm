# This file is placed in the Public Domain.
#
# pylint: disable=C0115,C0116,E0402,R0903


"log text"


import time


from ..objects import Object
from ..storage import find, fntime, write
from ..threads import laps


def __dir__():
    return (
            "Log",
            "log" 
           )


class Log(Object):

    def __init__(self):
        super().__init__()
        self.txt = ''


def log(event):
    if not event.rest:
        nmr = 0
        for obj in find('log'):
            lap = laps(time.time() - fntime(obj.__oid__))
            event.reply(f'{nmr} {obj.txt} {lap}')
            nmr += 1
        if not nmr:
            event.reply('no log')
        return
    obj = Log()
    obj.txt = event.rest
    write(obj)
    event.reply('ok')
