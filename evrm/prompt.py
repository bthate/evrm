# This file is placed in the Public Domain.
# pylint: disable=C0411,C0413,W0212,E0401


"prompt"


import os
import readline
import sys
import termios


from .console import Console
from .errors  import errors
from .persist import skel
from .main    import cmnd, enable, init, scan
from .parse   import parse
from .runtime import Cfg
from .utils   import forever, modnames, spl


from . import modules


if os.path.exists("mods"):
    import mods as MODS
else:
    MODS = None


def wrap(func):
    "reset console."
    old3 = None
    try:
        old3 = termios.tcgetattr(sys.stdin.fileno())
    except termios.error:
        pass
    try:
        func()
    except (KeyboardInterrupt, EOFError):
        print("")
    finally:
        if old3:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old3)
    errors()


def main():
    "main"
    parse(Cfg, " ".join(sys.argv[1:]))
    Cfg.dis = Cfg.sets.dis
    mods = modnames(modules, MODS)
    Cfg.mod = ",".join(mods)
    if Cfg.dis:
        Cfg.mod = ",".join(set(mods) - set(spl(Cfg.dis)))
    readline.redisplay()
    enable(print)
    skel()
    scan(Cfg.mod, modules, MODS)
    csl = Console(print, input)
    if "i" in Cfg.opts:
        init(Cfg.mod, modules,MODS)
    csl.start()
    cmnd(Cfg.otxt, print)
    forever()


def wrapped():
    "wrap main function."
    wrap(main)


if __name__ == "__main__":
    wrapped()
