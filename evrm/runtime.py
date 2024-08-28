# This file is placed in the Public Domain.


"runtime"


import getpass
import os
import time


from .config  import Config
from .persist import Persist


STARTTIME   = time.time()


Cfg         = Config()
Cfg.name    = Config.__module__.rsplit(".", maxsplit=1)[-2]
Cfg.user    = getpass.getuser()
Cfg.mod     = "cmd,skl,req,srv"
Cfg.wdr     = os.path.expanduser(f"~/.{Cfg.name}")
Cfg.pidfile = os.path.join(Cfg.wdr, f"{Cfg.name}.pid")


Persist.workdir = Cfg.wdr
