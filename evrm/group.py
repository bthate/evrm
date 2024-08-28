# This file is placed in the Public Domain.
# pylint: disable=R0903


"collection"


from .object import Object


class Group(Object):

    "Group"


def __dir__():
    return (
        'Group',
    )
