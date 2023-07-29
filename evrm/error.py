# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R,W0212,W0718,E0402


"logging"


import io
import traceback


from .utils import skip


class Error:

    skip = 'PING,PONG,PRIVMSG'
    verbose = False
    errors = []

    @staticmethod
    def debug(txt) -> None:
        if Error.verbose and not skip(txt, Error.skip):
            Error.raw(txt)

    @staticmethod
    def handle(exc):
        excp = exc.with_traceback(exc.__traceback__)
        Error.errors.append(excp)

    @staticmethod
    def raw(txt) -> None:
        pass


def waiter():
    got = []
    for ex in Error.errors:
        stream = io.StringIO(
                             traceback.print_exception(
                                                       type(ex),
                                                       ex,
                                                       ex.__traceback__
                                                      )
                            )
        for line in stream.readlines():
            Error.debug(line)
        got.append(ex)
    for exc in got:
        if exc in Error.errors:
            Error.errors.remove(exc)
