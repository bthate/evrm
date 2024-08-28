# This file is placed in the Public Domain.
# pylint: disable=C0413,W0212,W0613,W0718,E0401


"cli"


import getpass
import os
import sys


from .cmds    import Commands
from .persist import skel
from .errors  import errors, later
from .main    import cmnd, enable, scan
from .parse   import parse
from .runtime import Cfg
from .utils   import modnames


from . import modules


def srv(event):
    "create service file (pipx)."
    if event.args:
        username = event.args[0]
    else:
        username  = getpass.getuser()
    path = os.path.normpath(f"/home/{username}/.local/bin/")
    txt = f"""[Unit]
Description={Cfg.name.upper()}
Requires=network-online.target
After=network-online.target

[Service]
Type=simple
User={username}
Group={username}
ExecStartPre={path}/{Cfg.name} skl
ExecStart={path}/{Cfg.name}d
ExitType=cgroup
KillSignal=SIGKILL
KillMode=control-group
RemainAfterExit=yes
Restart=no

[Install]
WantedBy=default.target"""
    event.reply(txt)


def wrapped():
    "wrap main function."
    wrap(main)


def wrap(func):
    "catch exceptions"
    try:
        func()
    except (KeyboardInterrupt, EOFError):
        print("")
    except Exception as exc:
        later(exc)
    errors()


def main():
    "main"
    Commands.add(srv)
    parse(Cfg, " ".join(sys.argv[1:]))
    skel()
    enable(print)
    Cfg.dis = Cfg.sets.dis
    Cfg.mod = ",".join(modnames(modules))
    scan(Cfg.mod, modules)
    cmnd(Cfg.otxt, print)


if __name__ == "__main__":
    wrapped()
