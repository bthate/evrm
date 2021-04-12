# This file is placed in the Public Domain.

"output"

from .err import ENOTIMPLEMENTED
from .obj import Object
from .thr import launch
from .zzz import queue, time

class Output(Object):

    def __init__(self):
        super().__init__()
        self.oqueue = queue.Queue()
        self.sleep = 5.0

    def dosay(self, channel, txt):
        raise ENOTIMPLEMENTED("dosay")

    def output(self):
        while not self.stopped:
            channel, txt = self.oqueue.get()
            if self.stopped or not channel:
                break
            self.dosay(channel, txt)
            time.sleep(self.sleep)

    def say(self, channel, txt):
        self.oqueue.put_nowait((channel, txt))

    def start(self):
        self.stopped = False
        launch(self.output)
        return self

    def stop(self):
        self.stopped = True
        self.oqueue.put_nowait((None, None))
