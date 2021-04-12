# This file is in the Public Domain.

"repeater"

import time
import threading

from .obj import Object, getname
from .thr import launch

class Timer(Object):

    def __init__(self, sleep, func, name=None):
        super().__init__()
        self.func = func
        self.sleep = sleep
        self.name = name or  ""
        self.state = Object()
        self.timer = None

    def run(self):
        self.state.latest = time.time()
        launch(self.func)

    def start(self):
        if not self.name:
            self.name = getname(self.func)
        timer = threading.Timer(self.sleep, self.run)
        timer.setName(self.name)
        timer.setDaemon(True)
        timer.sleep = self.sleep
        timer.state = self.state
        timer.state.starttime = time.time()
        timer.state.latest = time.time()
        timer.func = self.func
        timer.start()
        self.timer = timer
        return timer

    def stop(self):
        if self.timer:
            self.timer.cancel()

class Repeater(Timer):

    def run(self):
        thr = launch(self.start)
        super().run()
        return thr
