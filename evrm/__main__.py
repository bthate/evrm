# This file is placed in the Public Domain.


"main"


import sys


from .errors  import errors
from .persist import skel
from .main    import cmnd, enable, scan, wrap
from .parse   import parse
from .runtime import Cfg
from .utils   import modnames


from . import modules


def main():
    "main"
    parse(Cfg, " ".join(sys.argv[1:]))
    skel()
    enable(print)
    Cfg.dis = Cfg.sets.dis
    Cfg.mod += "," + ",".join(modnames(modules))
    scan(Cfg.mod, modules)
    cmnd(Cfg.otxt, print)


def wrapped():
    "wrap main"
    wrap(main)
    errors()


if __name__ == "__main__":
    wrapped()
    