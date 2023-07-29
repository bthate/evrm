# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R,W0212,W0718,E0402,W0201


"event"


import threading


from .object import Default
from .parser import parse


class Event(Default):

    def __init__(self):
        Default.__init__(self)
        self._ready = threading.Event()
        self._thr = None
        self.args = []
        self.cmd = ""
        self.gets = {}
        self.mods = ""
        self.opts = ""
        self.rest = ""
        self.sets = {}
        self.result = []

    def parse(self, txt=None) -> None:
        parse(self, txt or self.txt or "")

    def ready(self) -> None:
        self._ready.set()

    def reply(self, txt) -> None:
        self.result.append(txt)

    def wait(self) -> []:
        if self._thr:
            self._thr.join()
        self._ready.wait()
        return self.result
