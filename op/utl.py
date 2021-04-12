# This file is placed in the Public Domain.

"utilities"

import getpass
import importlib
import os
import pwd
import sys

def cprint(txt):
    from .bus import first 
    k = first()
    if k.op("v"):
        sys.stdout.write(str(txt) + "\n")
        sys.stdout.flush()

def direct(name, pname=''):
    if name in sys.modules:
        return sys.modules[name]
    return importlib.import_module(name, pname)

def hasmod(fqn):
    try:
        spec = importlib.util.find_spec(fqn)
        if spec:
            return True
    except (ValueError, ModuleNotFoundError):
        pass
    return False

def locked(l):
    def lockeddec(func, *args, **kwargs):
        def lockedfunc(*args, **kwargs):
            l.acquire()
            res = None
            try:
                res = func(*args, **kwargs)
            finally:
                l.release()
            return res
        lockedfunc.__wrapped__ = func
        return lockedfunc
    return lockeddec

def privileges(name=None):
    if os.getuid() != 0:
        return
    if name is None:
        try:
            name = getpass.getuser()
        except KeyError:
            pass
    try:
        pwnam = pwd.getpwnam(name)
    except KeyError:
        return False
    os.setgroups([])
    os.setgid(pwnam.pw_gid)
    os.setuid(pwnam.pw_uid)
    old_umask = os.umask(0o22)
    return True

def root():
    if os.geteuid() != 0:
        return False
    return True

def spl(txt):
    return [x for x in txt.split(",") if x]
