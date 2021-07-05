# This file is placed in the Public Domain.

"python3 object library"

import atexit
import builtins
import datetime
import getpass
import importlib
import inspect
import json as js
import os
import pathlib
import pkgutil
import pwd
import queue
import readline
import sys
import termios
import threading
import time
import types
import uuid

resume = {}
wd = ".ob"

class Restart(Exception):

    pass

class NotImplemented(Exception):

    pass

class Restart(Exception):

    pass

class Stop(Exception):

    pass

class NoBot(Exception):

    pass


class NoFile(Exception):

    pass

class NoModule(Exception):

    pass

class NoType(Exception):

    pass

def cdir(path):
    if os.path.exists(path):
        return
    if path.split(os.sep)[-1].count(":") == 2:
        path = os.path.dirname(path)
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)

def gettype(o):
    return str(type(o)).split()[-1][1:-2]

def kernel():
    return getattr(sys.modules["__main__"], "k", None)

class O:

    __slots__ = ("__dict__", "__stp__", "__otype__")

    def __init__(self):
        self.__otype__ = gettype(self)
        self.__stp__ = os.path.join(gettype(self), str(uuid.uuid4()), os.sep.join(str(datetime.datetime.now()).split()))

    @staticmethod
    def __default__(oo):
        if isinstance(oo, O):
            return vars(oo)
        if isinstance(oo, dict):
            return oo.items()
        if isinstance(oo, list):
            return iter(oo)
        if isinstance(oo, (type(str), type(True), type(False), type(int), type(float))):
            return oo
        return O.__dorepr__(oo)

    @staticmethod
    def __dorepr__(o):
        return '<%s.%s object at %s>' % (
            o.__class__.__module__,
            o.__class__.__name__,
            hex(id(o))
        )
    def __delitem__(self, k):
        if k in self:
            del self.__dict__[k]

    def __getitem__(self, k):
        return self.__dict__[k]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __lt__(self, o):
        return len(self) < len(o)

    def __setitem__(self, k, v):
        self.__dict__[k] = v

    def __repr__(self):
        return js.dumps(self, default=self.__default__)
     
    def __str__(self):
        return str(self.__dict__)

class Obj(O):

    def __init__(self, *args, **kwargs):
        super().__init__()
        if args:
            self.update(args[0])

    def delkeys(self, keys=[]):
        for k in keys:
            del self[k]

    def edit(self, setter, skip=True, skiplist=[]):
        count = 0
        for key, v in setter.items():
            if skip and v == "":
                continue
            if key in skiplist:
                continue
            count += 1
            if v in ["True", "true"]:
                self[key] = True
            elif v in ["False", "false"]:
                self[key] = False
            else:
                self[key] = v
        return count

    def get(self, key, default=None):
        return self.__dict__.get(key, default)

    def keys(self):
        return self.__dict__.keys()

    def items(self):
        return self.__dict__.items()

    def last(self):
        db = Db()
        t = str(gettype(self))
        path, l = db.lastfn(t)
        if  l:
            self.update(l)
        if path:
            spl = path.split(os.sep)
            stp = os.sep.join(spl[-4:])
            return stp

    def merge(self, d):
        for k, v in d.items():
            if not v:
                continue
            if k in self:
                if isinstance(self[k], dict):
                    continue
                self[k] = self[k] + v
            else:
                self[k] = v

    def overlay(self, d, keys=None, skip=None):
        for k, v in d.items():
            if keys and k not in keys:
                continue
            if skip and k in skip:
                continue
            if v:
                self[k] = v

    def register(self, key, value):
        self[str(key)] = value

    def search(o, s):
        ok = False
        for k, v in s.items():
            vv = getattr(o, k, None)
            if v not in str(vv):
                ok = False
                break
            ok = True
        return ok

    def set(self, key, value):
        self.__dict__[key] = value

    def update(self, data):
        return self.__dict__.update(data)

    def values(self):
        return self.__dict__.values()

class Object(Obj):

    def json(self):
        return repr(self)

    def load(self, opath):
        assert wd
        if opath.count(os.sep) != 3:
            raise NoFile(opath)
        spl = opath.split(os.sep)
        stp = os.sep.join(spl[-4:])
        lpath = os.path.join(wd, "store", stp)
        if os.path.exists(lpath):
            with open(lpath, "r") as ofile:
                d = js.load(ofile, object_hook=Obj)
                self.update(d)
        self.__stp__ = stp
        return self

    def save(self, tab=False):
        assert wd
        prv = os.sep.join(self.__stp__.split(os.sep)[:2])
        self.__stp__ = os.path.join(prv, os.sep.join(str(datetime.datetime.now()).split()))
        opath = os.path.join(wd, "store", self.__stp__)
        cdir(opath)
        with open(opath, "w") as ofile:
            js.dump(self, ofile, default=self.__default__, indent=4, sort_keys=True)
        os.chmod(opath, 0o444)
        return self.__stp__

class Default(Object):

    default = ""

    def __getattr__(self, k):
        if k in self:
            return super().__getattribute__(k)
        if k in super().__dict__:
            return super().__getitem__(k)
        return self.default

class Cfg(Default):

    pass

class List(Object):

    def append(self, key, value):
        if key not in self:
            self[key] = []
        if value in self[key]:
            return
        if isinstance(value, list):
            self[key].extend(value)
        else:
            self[key].append(value)

    def update(self, d):
        for k, v in d.items():
            self.append(k, v)

class Timer(Object):

    def __init__(self, sleep, func, *args, name=None):
        super().__init__()
        self.args = args
        self.func = func
        self.sleep = sleep
        self.name = name or  ""
        self.state = Object()
        self.timer = None

    def run(self):
        self.state.latest = time.time()
        launch(self.func, *self.args)

    def start(self):
        if not self.name:
            self.name = getname(self.func)
        timer = threading.Timer(self.sleep, self.run)
        timer.setName(self.name)
        timer.setDaemon(True)
        timer.sleep = self.sleep
        timer.state = self.state
        timer.state.starttime = time.time()
        timer.state.latest = time.time()
        timer.func = self.func
        timer.start()
        self.timer = timer
        return timer

    def stop(self):
        if self.timer:
            self.timer.cancel()

class Repeater(Timer):

    def run(self):
        thr = launch(self.start)
        super().run()
        return thr


class Db(Object):

    def all(self, otype, selector=None, index=None, timed=None):
        nr = -1
        if selector is None:
            selector = {}
        for fn in fns(otype, timed):
            o = hook(fn)
            if selector and not o.search(selector):
                continue
            if "_deleted" in o and o._deleted:
                continue
            nr += 1
            if index is not None and nr != index:
                continue
            yield fn, o

    def deleted(self, otype):
        for fn in fns(otype):
            o = hook(fn)
            if "_deleted" not in o or not o._deleted:
                continue
            yield fn, o

    def every(self, selector=None, index=None, timed=None):
        k = kernel()
        if selector is None:
            selector = {}
        nr = -1
        for otype in os.listdir(os.path.join(wd, "store")):
            for fn in fns(otype, timed):
                o = hook(fn)
                if selector and not o.search(selector):
                    continue
                if "_deleted" in o and o._deleted:
                    continue
                nr += 1
                if index is not None and nr != index:
                    continue
                yield fn, o

    def find(self, otype, selector=None, index=None, timed=None):
        if selector is None:
            selector = {}
        got = False
        nr = -1
        for fn in fns(otype, timed):
            o = hook(fn)
            if selector and not o.search(selector):
                continue
            if "_deleted" in o and o._deleted:
                continue
            nr += 1
            if index is not None and nr != index:
                continue
            got = True
            yield (fn, o)
        if not got:
            return (None, None)

    def lastmatch(self, otype, selector=None, index=None, timed=None):
        res = sorted(self.find(otype, selector, index, timed), key=lambda x: fntime(x[0]))
        if res:
            return res[-1]
        return (None, None)

    def lasttype(self, otype):
        fnn = fns(otype)
        if fnn:
            return hook(fnn[-1])

    def lastfn(self, otype):
        fn = fns(otype)
        if fn:
            fnn = fn[-1]
            return (fnn, hook(fnn))
        return (None, None)

class Thr(threading.Thread):

    def __init__(self, func, *args, thrname="", daemon=True):
        super().__init__(None, self.run, thrname, (), {}, daemon=daemon)
        self.name = thrname or getname(func)
        self.result = None
        self.queue = queue.Queue()
        self.queue.put_nowait((func, args))
        self.sleep = 0

    def __iter__(self):
        return self

    def __next__(self):
        for k in dir(self):
            yield k

    def join(self, timeout=None):
        ""
        super().join(timeout)
        return self.result

    def run(self):
        ""
        func, args = self.queue.get_nowait()
        if args:
            target = vars(args[0])
            if target and "txt" in dir(target):
                self.name = target.txt.split()[0]
        self.setName(self.name)
        self.result = func(*args)

class Token(Object):

    def __init__(self, txt):
        super().__init__()
        self.txt = txt

class Option(Default):

    def __init__(self, txt):
        super().__init__()
        if txt.startswith("--"):
            self.opt = txt[2:]
        if txt.startswith("-"):
            self.opt = txt[1:]

class Getter(Object):

    def __init__(self, txt):
        super().__init__()
        if "==" in txt:
            pre, post = txt.split("==", 1)
        else:
            pre = post = ""
        if pre:
            self[pre] = post

class Setter(Object):

    def __init__(self, txt):
        super().__init__()
        if "=" in txt:
            pre, post = txt.split("=")
        else:
            pre = post = ""
        if pre:
            self[pre] = post

class Skip(Object):

    def __init__(self, txt):
        super().__init__()
        pre = ""
        if txt.endswith("-"):
            if "=" in txt:
                pre, _post = txt.split("=", 1)
            elif "==" in txt:
                pre, _post = txt.split("==", 1)
            else:
                pre = txt
        if pre:
            self[pre] = True

class Url(Object):

    def __init__(self, txt):
        super().__init__()
        if txt.startswith("http"):
            self["url"] = txt

class Bus(Object):

    objs = []

    def __iter__(self):
        return iter(Bus.objs)

    @staticmethod
    def add(obj):
        if obj not in Bus.objs:
            Bus.objs.append(obj)

    @staticmethod
    def announce(txt):
        for h in Bus.objs:
            if "announce" in dir(h):
                h.announce(txt)

    @staticmethod
    def byorig(orig):
        for o in Bus.objs:
            if Object.__dorepr__(o) == orig:
                return o

    @staticmethod
    def byfd(fd):
        for o in Bus.objs:
            if o.fd and o.fd == fd:
                return o

    @staticmethod
    def bytype(typ):
        for o in Bus.objs:
            if isinstance(o, type):
                return o

    def first(otype=None):
        if Bus.objs:
            if not otype:
                return Bus.objs[0]
            for o in Bus.objs:
                if otype in str(type(o)):
                    return o

    @staticmethod
    def resume():
        for o in Bus.objs:
            o.resume()

    @staticmethod
    def say(orig, channel, txt):
        for o in Bus.objs:
            if Object.__dorepr__(o) == orig:
                o.say(channel, txt)

class Dispatcher(Object):

    def __init__(self):
        super().__init__()
        self.cbs = Object()

    def dispatch(self, event):
        if event and event.type in self.cbs:
            self.cbs[event.type](self, event)
        else:
            event.ready()

    def register(self, name, callback):
        self.cbs[name] = callback

class Output(Object):

    def __init__(self):
        Object.__init__(self)
        self.cache = List()
        self.oqueue = queue.Queue()
        self.dostop = threading.Event()
        
    @staticmethod
    def append(channel, txtlist):
        if channel not in Output.cache:
            self.cache[channel] = []
        self.cache[channel].extend(txtlist)

    def dosay(self, channel, txt):
        pass

    def oput(self, channel, txt):
        self.oqueue.put_nowait((channel, txt))

    def output(self):
        while not self.dostop.isSet():
            (channel, txt) = self.oqueue.get()
            if self.dostop.isSet() or channel is None:
                break
            self.dosay(channel, txt)

    @staticmethod
    def size(name):
        if name in self.cache:
            return len(self.cache[name])
        return 0

    def start(self):
        self.dostop.clear()
        launch(self.output)
        return self

    def stop(self):
        self.dostop.set()
        self.oqueue.put_nowait((None, None))

class Event(Default):

    def __init__(self):
        super().__init__()
        self.channel = None
        self.done = threading.Event()
        self.error = ""
        self.exc = None
        self.orig = None
        self.result = []
        self.thrs = []
        self.type = "event"
        self.txt = None

    def bot(self):
        return Bus.byorig(self.orig)

    def parse(self):
        if self.txt is not None:
            parse_txt(self, self.txt)

    def ready(self):
        self.done.set()

    def reply(self, txt):
        self.result.append(txt)

    def say(self, txt):
        Bus.say(self.orig, self.channel, txt.rstrip())

    def show(self):
        if self.exc:
            self.say(self.exc)
            return
        bot = self.bot()
        if not bot:
            raise NoBot(self.orig)
        if bot.speed == "slow" and len(self.result) > 3:
            Output.append(self.channel, self.result)
            self.say("%s lines in cache, use !mre" % len(self.result))
            return
        for txt in self.result:
            self.say(txt)

    def wait(self, timeout=1.0):
        self.done.wait(timeout)
        for thr in self.thrs:
            thr.join(timeout)

class Command(Event):

    def __init__(self):
        super().__init__()
        self.type = "cmd"

class Loop(Object):

    def __init__(self):
        super().__init__()
        self.queue = queue.Queue()
        self.speed = "normal"
        self.stopped = threading.Event()

    def do(self, e):
        raise NotImplemented("do")
        
    def error(self, e):
        raise NotImplemented("error")

    def loop(self):
        dorestart = False
        self.stopped.clear()
        while not self.stopped.isSet():
            e = self.queue.get()
            try:
                self.do(e)
            except Restart:
                dorestart = True
                break
            except Stop:
                break
            except Exception as ex:
                e = Event()
                e.type = "error"
                e.exc = ex
                self.error(e)
        if dorestart:
            self.restart()

    def restart(self):
        self.stop()
        self.start()

    def put(self, e):
        self.queue.put_nowait(e)

    def restart(self):
        self.stop()
        self.start()

    def start(self):
        launch(self.loop)
        return self

    def stop(self):
        self.stopped.set()
        self.queue.put(None)

class Handler(Dispatcher, Loop):

    def cmd(self, txt):
        Bus.add(self)
        e = self.event(txt)
        e.origin = "root@shell"
        self.dispatch(e)
        e.wait()

    def event(self, txt):
        if txt is None:
            return
        c = Command()
        c.txt = txt or ""
        c.orig = Object.__dorepr__(self)
        return c

    def handle(self, e):
        raise NotImplemented("handle")

    def loop(self):
        while not self.stopped.isSet():
            txt = self.poll()
            if txt is None:
                break
            e = self.event(txt)
            if not e:
                break
            self.handle(e)

    def poll(self):
        return self.queue.get()

    def raw(self, txt):
        pass

    def say(self, channel, txt):
        self.raw(txt)

    def start(self):
        super().start()
        Bus.add(self)

class Kernel(Dispatcher, Loop):

    def __init__(self):
        Dispatcher.__init__(self)
        Loop.__init__(self)
        self.cfg = Cfg()
        self.cmds = Object()
        self.register("cmd", self.handle)

    def add(self, func):
        n = func.__name__
        self.cmds[n] = func

    def boot(self, wd=""):
        self.parse_cli(wd)
        cdir(self.cfg.wd + os.sep)
        self.scan(self.cfg.p)
        self.init(self.cfg.m)

    def cmd(self, clt, txt):
        Bus.add(clt)
        e = clt.event(txt)
        e.origin = "root@shell"
        self.dispatch(e)
        e.wait()

    def do(self, e):
        self.dispatch(e)

    def error(self, e):
        pass

    def handle(self, hdl, obj):
        obj.parse()
        f = self.cmds.get(obj.cmd, None)
        if f:
            f(obj)
            obj.show()
        obj.ready()

    def init(self, mns):
        for mn in spl(mns):
            mod = sys.modules.get(mn, None)
            i = getattr(mod, "init", None)
            if i:
                launch(i, self)

    def introspect(self, mod):
        for key, o in inspect.getmembers(mod, inspect.isfunction):
            if o.__code__.co_argcount == 1 and "event" in o.__code__.co_varnames:
                self.cmds[o.__name__] = o

    def opts(self, ops):
        for opt in ops:
            if opt in self.cfg.opts:
                return True
        return False

    def parse_cli(self, wd=""):
        txt = " ".join(sys.argv[1:])
        o = Default()
        parse_txt(o, txt)
        self.cfg.update(o)
        self.cfg.update(self.cfg.sets)
        wd = wd or self.cfg.wd or wd or None

    @staticmethod
    def privileges(name=None):
        if os.getuid() != 0:
            return
        try:
            pwn = pwd.getpwnam(name)
        except KeyError:
            name = getpass.getuser()
            try:
                pwn = pwd.getpwnam(name)
            except KeyError:
                return
        if name is None:
            try:
                name = getpass.getuser()
            except KeyError:
                pass
        try:
            pwn = pwd.getpwnam(name)
        except KeyError:
            return False
        try:
            os.chown(wd, pwn.pw_uid, pwn.pw_gid)
        except PermissionError:
            pass
        os.setgroups([])
        os.setgid(pwnam.pw_gid)
        os.setuid(pwnam.pw_uid)
        old_umask = os.umask(0o22)
        return True

    @staticmethod
    def root():
        if os.geteuid() != 0:
            return False
        return True

    def scan(self, pkgs=""):
        res = {}
        for pn in spl(pkgs):
            p = sys.modules.get(pn, None)
            if not p:
                try:
                    p = __import__(pn)
                except ModuleNotFoundError:
                    continue
            for mn in pkgutil.walk_packages(p.__path__, pn+"."):
                zip = mn[0].find_module(mn[1])
                mod = zip.load_module(mn[1])
                self.introspect(mod)
                
    def start(self, wd=""):
        self.boot(wd)
        super().start()

    @staticmethod
    def wait():
        while 1:
            time.sleep(5.0)

k = Kernel()

class CLI(Handler):

    def error(self, e):
        print(e.exc)
        raise Restart

    def handle(self, e):
        k.put(e)
        e.wait()

    def raw(self, txt):
        print(txt)

class Console(CLI):

    def error(self, e):
        print(e.exc)
        raise Restart

    def handle(self, e):
        k.put(e)
        e.wait()

    def poll(self):
        return input("> ")

    def raw(self, txt):
        print(txt)

def day():
    return str(datetime.datetime.today()).split()[0]

def elapsed(seconds, short=True):
    txt = ""
    nsec = float(seconds)
    year = 365*24*60*60
    week = 7*24*60*60
    nday = 24*60*60
    hour = 60*60
    minute = 60
    years = int(nsec/year)
    nsec -= years*year
    weeks = int(nsec/week)
    nsec -= weeks*week
    nrdays = int(nsec/nday)
    nsec -= nrdays*nday
    hours = int(nsec/hour)
    nsec -= hours*hour
    minutes = int(nsec/minute)
    sec = nsec - minutes*minute
    if years:
        txt += "%sy" % years
    if weeks:
        nrdays += weeks * 7
    if nrdays:
        txt += "%sd" % nrdays
    if years and short and txt:
        return txt
    if hours:
        txt += "%sh" % hours
    if nrdays and short and txt:
        return txt
    if minutes:
        txt += "%sm" % minutes
    if hours and short and txt:
        return txt
    if sec == 0:
        txt += "0s"
    else:
        txt += "%ss" % int(sec)
    txt = txt.strip()
    return txt

def fmt(o, keys=None, empty=True, skip=None):
    if keys is None:
        keys = o.keys()
    if not keys:
        keys = ["txt"]
    if skip is None:
        skip = []
    res = []
    txt = ""
    for key in sorted(keys):
        if key in skip:
            continue
        if key in o:
            val = o[key]
            if empty and not val:
                continue
            val = str(val).strip()
            res.append((key, val))
    result = []
    for k, v in res:
        result.append("%s=%s%s" % (k, v, " "))
    txt += " ".join([x.strip() for x in result])
    return txt.strip()

def fns(name, timed=None):
    if not name:
        return []
    p = os.path.join(wd, "store", name) + os.sep
    res = []
    d = ""
    for rootdir, dirs, _files in os.walk(p, topdown=False):
        if dirs:
            d = sorted(dirs)[-1]
            if d.count("-") == 2:
                dd = os.path.join(rootdir, d)
                fls = sorted(os.listdir(dd))
                if fls:
                    p = os.path.join(dd, fls[-1])
                    if timed and "from" in timed and timed["from"] and fntime(p) < timed["from"]:
                        continue
                    if timed and timed.to and fntime(p) > timed.to:
                        continue
                    res.append(p)
    return sorted(res, key=fntime)


def fntime(daystr):
    daystr = daystr.replace("_", ":")
    datestr = " ".join(daystr.split(os.sep)[-2:])
    if "." in datestr:
        datestr, rest = datestr.rsplit(".", 1)
    else:
        rest = ""
    t = time.mktime(time.strptime(datestr, "%Y-%m-%d %H:%M:%S"))
    if rest:
        t += float("." + rest)
    else:
        t = 0
    return t

def getname(o):
    t = type(o)
    if t == types.ModuleType:
        return o.__name__
    if "__self__" in dir(o):
        return "%s.%s" % (o.__self__.__class__.__name__, o.__name__)
    if "__class__" in dir(o) and "__name__" in dir(o):
        return "%s.%s" % (o.__class__.__name__, o.__name__)
    if "__class__" in dir(o):
        return o.__class__.__name__
    if "__name__" in dir(o):
        return o.__name__

def hook(hfn):
    if hfn.count(os.sep) > 3:
        oname = hfn.split(os.sep)[-4:]
    else:
        oname = hfn.split(os.sep)
    cname = oname[0]
    fn = os.sep.join(oname)
    mn, cn = cname.rsplit(".", 1)
    mod = sys.modules.get(mn, None)
    if not mod:
        raise NoModule(mn)        
    t = getattr(mod, cn, None)
    if fn:
        o = t()
        o.load(fn)
        return o
    raise NoType(cname)

def launch(func, *args, **kwargs):
    name = kwargs.get("name", getname(func))
    t = Thr(func, *args, thrname=name, daemon=True)
    t.start()
    return t

def spl(txt):
    return [x for x in txt.split(",") if x]

def listfiles(wd):
    path = os.path.join(wd, "store")
    if not os.path.exists(path):
        return []
    return sorted(os.listdir(path))

def parse_txt(o, ptxt=None):
    if ptxt is None:
        raise NoTextError(o)
    o.txt = ptxt
    o.otxt = ptxt
    o.gets = o.gets or Default()
    o.opts = o.opts or Default()
    o.timed = []
    o.index = None
    o.sets = o.sets or Default()
    o.skip = o.skip or Default()
    args = []
    for token in [Token(txt) for txt in ptxt.split()]:
        u = Url(token.txt)
        if u:
            args.append(u.url)
            continue
        s = Skip(token.txt)
        if s:
            o.skip.update(s)
            token.txt = token.txt[:-1]
        g = Getter(token.txt)
        if g:
            o.gets.update(g)
            continue
        s = Setter(token.txt)
        if s:
            o.sets.update(s)
            continue
        opt = Option(token.txt)
        if opt:
            try:
                o.index = int(opt.opt)
                continue
            except ValueError:
                pass
            if len(opt.opt) > 1:
                for op in opt.opt:
                    o.opts[op] = True
            else:
                o.opts[opt.opt] = True
            continue
        args.append(token.txt)
    if not args:
        o.args = []
        o.cmd = ""
        o.rest = ""
        o.txt = ""
        return o
    o.cmd = args[0]
    o.args = args[1:]
    o.txt = " ".join(args)
    o.rest = " ".join(args[1:])
    return o

def parse_ymd(daystr):
    valstr = ""
    val = 0
    total = 0
    for c in daystr:
        if c in "1234567890":
            vv = int(valstr)
        else:
            vv = 0
        if c == "y":
            val = vv * 3600*24*365
        if c == "w":
            val = vv * 3600*24*7
        elif c == "d":
            val = vv * 3600*24
        elif c == "h":
            val = vv * 3600
        elif c == "m":
            val = vv * 60
        else:
            valstr += c
        total += val
    return total
