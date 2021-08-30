# This file is placed in the Public Domain.

import threading

from .bus import Bus
from .obj import Object
from .opt import Output
from .prs import parse_txt


class ENoBot(Exception):

    pass


class Event(Object):

    def __init__(self):
        super().__init__()
        self.channel = None
        self.done = threading.Event()
        self.error = ""
        self.handler = None
        self.exc = None
        self.orig = None
        self.result = []
        self.thrs = []
        self.type = "event"
        self.txt = None

    def bot(self):
        return Bus.byorig(self.orig)

    def parse(self):
        parse_txt(self, self.txt)

    def ready(self):
        self.done.set()

    def reply(self, txt):
        self.result.append(txt)

    def say(self, txt):
        Bus.say(self.orig, self.channel, txt)

    def show(self):
        bot = self.bot()
        if not bot:
            raise ENoBot(self.orig)
        if bot.speed == "slow" and len(self.result) > 3:
            Output.append(self.channel, self.result)
            self.say("%s lines in cache, use !mre" % len(self.result))
            return
        for txt in self.result:
            self.say(txt)

    def wait(self, timeout=1.0):
        self.done.wait(timeout)
        for thr in self.thrs:
            thr.join(timeout)


class Error(Event):

    pass


class Command(Event):

    def __init__(self):
        super().__init__()
        self.type = "cmd"
