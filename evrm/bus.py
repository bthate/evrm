# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R


"bus"


class Bus:

    objs = []

    @staticmethod
    def add(obj) -> None:
        Bus.objs.append(obj)

    @staticmethod
    def announce(txt) -> None:
        for obj in Bus.objs:
            obj.announce(txt)

    @staticmethod
    def byorig(orig):
        for obj in Bus.objs:
            if repr(obj) == orig:
                return obj
        return None

    @staticmethod
    def remove(obj) -> None:
        try:
            Bus.objs.remove(obj)
        except ValueError:
            pass

    @staticmethod
    def say(orig, txt, channel=None) -> None:
        obj = Bus.byorig(orig)
        if obj:
            if channel:
                obj.say(channel, txt)
            else:
                obj.raw(txt)

    @staticmethod
    def show(event) -> None:
        for txt in event.result:
            Bus.say(event.orig, txt, event.channel)
