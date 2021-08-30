# This file is placed in the Public Domain.

import queue
import threading

from .obj import List, Object
from .thr import launch

class Output(Object):

    cache = List()

    def __init__(self):
        Object.__init__(self)
        self.oqueue = queue.Queue()
        self.dostop = threading.Event()

    @staticmethod
    def append(channel, txtlist):
        if channel not in Output.cache:
            Output.cache[channel] = []
        Output.cache[channel].extend(txtlist)

    def dosay(self, channel, txt):
        pass

    def oput(self, channel, txt):
        self.oqueue.put_nowait((channel, txt))

    def output(self):
        while not self.dostop.isSet():
            (channel, txt) = self.oqueue.get()
            if self.dostop.isSet() or channel is None:
                break
            self.dosay(channel, txt)

    @staticmethod
    def size(name):
        if name in Output.cache:
            return len(Output.cache[name])
        return 0

    def start(self):
        self.dostop.clear()
        launch(self.output)
        return self

    def stop(self):
        self.dostop.set()
        self.oqueue.put_nowait((None, None))
