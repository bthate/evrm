# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R


"errors"


import io
import traceback


from ..error import Error


def __dir__():
    return (
            'err',
           )


__all__ = __dir__()


def err(event):
    nmr = 0
    for exc in Error.errors:
        nmr += 1
        stream = io.StringIO(
                             traceback.print_exception(
                                                       type(exc),
                                                       exc,
                                                       exc.__traceback__
                                                      )
                            )
        for line in stream.readlines():
            event.reply(line)
    if not nmr:
        event.reply("no error")
