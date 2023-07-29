# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R,W0212,W0611
# flake8: noqa


"runtime"


import os


NAME  = __file__.split(os.sep)[-2]
VERSION = 30
WORKDIR = os.path.expanduser(f"~/.{NAME}")


import sys


sys.path.insert(0, os.getcwd())


import readline
import termios
import threading
import time
import _thread


from .bus     import Bus
from .command import Command, scan
from .error   import Error, waiter
from .event   import Event
from .object  import printable
from .parser  import parse
from .persist import Persist
from .reactor import Reactor
from .run     import Cfg
from .thread  import launch
from .utils   import wait
from .        import modules


Cfg.mod = "cmd,err,log,sts,tdo,thr"
Persist.workdir = WORKDIR


class CLI(Reactor):

    def __init__(self):
        Reactor.__init__(self)
        Bus.add(self)
        self.register("event", Command.handle)

    def announce(self, txt):
        pass

    def raw(self, txt):
        print(txt)
        sys.stdout.flush()


class Console(CLI):


    prompting = threading.Event()

    def __init__(self):
        CLI.__init__(self)

    def handle(self, evt):
        Command.handle(evt)
        evt.wait()

    def prompt(self):
        self.prompting.set()
        x = input("> ")
        self.prompting.clear()
        return x
        
    def poll(self):
        try:
            return self.event(self.prompt())
        except EOFError:
            _thread.interrupt_main()
      

def banner(cfg):
    cfgg = printable(cfg, skip="otxt,password")
    return f"{NAME.upper()} {VERSION} {cfgg}"


def cprint(txt):
    if Console.prompting.is_set():
        txt = "\n" + txt
    print(txt)
    Console.prompting.clear()
    sys.stdout.flush()

def daemon():
    pid = os.fork()
    if pid != 0:
        os._exit(0)
    os.setsid()
    os.umask(0)
    sis = open('/dev/null', 'r', encoding="utf-8")
    os.dup2(sis.fileno(), sys.stdin.fileno())
    sos = open('/dev/null', 'a+', encoding="utf-8")
    ses = open('/dev/null', 'a+', encoding="utf-8")
    os.dup2(sos.fileno(), sys.stdout.fileno())
    os.dup2(ses.fileno(), sys.stderr.fileno())


def wrap(func) -> None:
    old = termios.tcgetattr(sys.stdin.fileno())
    try:
        func()
    except (EOFError, KeyboardInterrupt):
        print("")
        sys.stdout.flush()
    finally:
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old)
    waiter()


def wrapped():
    wrap(main)


def main():
    parse(Cfg, " ".join(sys.argv[1:]))
    if "v" in Cfg.opts:
        Error.raw = cprint
        Error.verbose = True
    if "d" in Cfg.opts:
        daemon()
        scan(modules, Cfg.mod, True, "a" in Cfg.opts)
        wait()
    elif "c" in Cfg.opts:
        print(banner(Cfg))
        scan(modules, Cfg.mod, True, "a" in Cfg.opts, True)
        csl = Console()
        csl.start()
        wait()
    else:
        cli = CLI()
        scan(modules, Cfg.mod, False, True)
        evt = Event()
        evt.orig = repr(cli)
        evt.txt = Cfg.otxt
        evt._thr = launch(Command.handle, evt)
        evt.wait()

if __name__ == "__main__":
    wrapped()
