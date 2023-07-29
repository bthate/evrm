# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R
# flake8: noqa


"log text"


import time


from ..object  import Object
from ..persist import Persist, find, fntime, write
from ..utils   import laps


def __dir__():
    return (
            'log',
           )


__all__ = __dir__()


class Log(Object):

    def __init__(self):
        super().__init__()
        self.createtime = time.time()
        self.txt = ''

    def __size__(self):
        return len(self.txt)

    def __since__(self):
        return self.createtime


Persist.add(Log)


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
