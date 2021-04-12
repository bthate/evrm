# This file is in the Public Domain.

"event"

import threading

from .obj import Default
from .bus import Bus
from .prs import parseargs

class Event(Default):

    def __init__(self, val=None):
        super().__init__(val)
        self.channel = ""
        self.done = threading.Event()
        self.result = []
        self.thrs = []
        self.type = "event"

    def bot(self):
        return Bus.byorig(self.orig)

    def parse(self):
        parseargs(self, self.txt)
        return self

    def ready(self):
        self.done.set()

    def reply(self, txt):
        self.result.append(txt)

    def say(self, txt):
        try:
            Bus.say(self.orig, self.channel, txt.rstrip())
        except UnicodeEncodeError:
            pass

    def show(self):
        for txt in self.result:
            self.say(txt)

    def wait(self, timeout=1.0):
        self.done.wait()
        for thr in self.thrs:
            thr.join()

class Command(Event):

    def __init__(self, val):
        super().__init__(val)
        self.type = "cmd"

events = []
        