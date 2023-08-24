# This file is placed in the Public Domain.
#
# pylint: disable=C0116,E0402


"errors"


import io
import traceback


from ..reactor import Reactor
from ..threads import Thread


def __dir__():
    return (
            "err",
           )


def err(event):
    if not Reactor.errors and not Thread.errors:
        event.reply("no errors")
        return
    for exc in Reactor.errors + Thread.errors:
        stream = io.StringIO(
                             traceback.print_exception(
                                                       type(exc),
                                                       exc,
                                                       exc.__traceback__
                                                      )
                            )
        for line in stream.readlines():
            event.reply(line)
