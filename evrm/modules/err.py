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
    if not Error.errors:
        event.reply("no error")
        return
    for exc in Error.errors:
        stream = io.StringIO(
                             traceback.print_exception(
                                                       type(exc),
                                                       exc,
                                                       exc.__traceback__
                                                      )
                            )
        for line in stream.readlines():
            event.reply(line)
