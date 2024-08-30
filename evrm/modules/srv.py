# This file is placed in the Public Domain.


"service"


import getpass
import os


from ..runtime import Cfg


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
ExecStart={path}/{Cfg.name}s
ExitType=cgroup
KillSignal=SIGKILL
KillMode=control-group
Restart=no

[Install]
WantedBy=default.target"""
    event.reply(txt)


srv.target = "cli"
