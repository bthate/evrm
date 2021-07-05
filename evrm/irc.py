# This file is placed in the Public Domain.

import ob
import os
import queue
import socket
import textwrap
import time
import threading
import _thread

from ob import Bus, Default, Dispatcher, Event, Handler, Object, Output, kernel, launch, fmt

def __dir__():
    return ("Cfg", "DCC", "Event", "IRC", "User", "Users", "cfg", "dlt", "init", "locked", "met", "mre")

def init(k):
    i = IRC()
    launch(i.start)
    return i

k = kernel()

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

saylock = _thread.allocate_lock()

class Cfg(Default):

    cc = "!"
    channel = "#ob"
    nick = "ob"
    port = 6667
    server = "localhost"
    realname = "python3 object library"
    username = "ob"
    users = False

    def __init__(self, val=None):
        super().__init__()
        self.cc = Cfg.cc
        self.channel = Cfg.channel
        self.nick = Cfg.nick
        self.port = Cfg.port
        self.server = Cfg.server
        self.realname = Cfg.realname
        self.username = Cfg.username
        self.users = Cfg.users
        if val:
            self.update(val)

class Event(Event):

    pass

class TextWrap(textwrap.TextWrapper):

    def __init__(self):
        super().__init__()
        self.break_long_words = False
        self.drop_whitespace = False
        self.fix_sentence_endings = True
        self.replace_whitespace = True
        self.tabsize = 4
        self.width = 450

class IRC(Output, Handler):

    def __init__(self):
        Handler.__init__(self)
        Output.__init__(self)
        self.buffer = []
        self.cfg = Cfg()
        self.connected = threading.Event()
        self.channels = []
        self.sock = None
        self.joined = threading.Event()
        self.keeprunning = False
        self.outqueue = queue.Queue()
        self.speed = "slow"
        self.state = Object()
        self.state.needconnect = False
        self.state.error = ""
        self.state.last = 0
        self.state.lastline = ""
        self.state.nrconnect = 0
        self.state.nrerror = 0
        self.state.nrsend = 0
        self.state.pongcheck = False
        self.threaded = False
        self.users = Users()
        self.zelf = ""
        self.register("ERROR", ERROR)
        self.register("LOG", LOG)
        self.register("NOTICE", NOTICE)
        self.register("PRIVMSG", PRIVMSG)
        self.register("QUIT", QUIT)

    def announce(self, txt):
        for channel in self.channels:
            self.say(channel, txt)

    @locked(saylock)
    def command(self, cmd, *args):
        if not args:
            self.raw(cmd)
        elif len(args) == 1:
            self.raw("%s %s" % (cmd.upper(), args[0]))
        elif len(args) == 2:
            self.raw("%s %s :%s" % (cmd.upper(), args[0], " ".join(args[1:])))
        elif len(args) >= 3:
            self.raw("%s %s %s :%s" % (cmd.upper(), args[0], args[1], " ".join(args[2:])))
        if (time.time() - self.state.last) < 4.0:
            time.sleep(4.0)
        self.state.last = time.time()

    def connect(self, server, port=6667):
        addr = socket.getaddrinfo(server, port, socket.AF_INET)[-1][-1]
        self.sock = socket.create_connection(addr)
        os.set_inheritable(self.fileno(), os.O_RDWR)
        self.sock.setblocking(True)
        self.sock.settimeout(180.0)
        self.connected.set()
        return True

    def doconnect(self, server, nick, port=6667):
        self.state.nrconnect = 0
        while not self.stopped.isSet():
            self.state.nrconnect += 1
            if self.connect(server, port):
                break
            time.sleep(10.0 * self.state.nrconnect)
        self.logon(server, nick)

    def dosay(self, channel, txt):
        wrapper = TextWrap()
        txt = str(txt).replace("\n", "")
        for t in wrapper.wrap(txt):
            if not t:
                continue
            self.command("PRIVMSG", channel, t)

    def event(self, txt):
        if not txt:
            return
        e = self.parsing(txt)
        cmd = e.command
        if cmd == "PING":
            self.state.pongcheck = True
            self.command("PONG", e.txt or "")
        elif cmd == "PONG":
            self.state.pongcheck = False
        if cmd == "001":
            self.state.needconnect = False
            if "servermodes" in dir(self.cfg):
                self.raw("MODE %s %s" % (self.cfg.nick, self.cfg.servermodes))
            self.zelf = e.args[-1]
            self.joinall()
        elif cmd == "002":
            self.state.host = e.args[2][:-1]
        elif cmd == "366":
            self.joined.set()
        elif cmd == "433":
            nick = self.cfg.nick + "_"
            self.cfg.nick = nick
            self.raw("NICK %s" % self.cfg.nick)
        return e

    def fileno(self):
        return self.sock.fileno()

    def do(self, e):
        super().callbacks(e)

    def joinall(self):
        for channel in self.channels:
            self.command("JOIN", channel)

    def handle(self, e):
        self.dispatch(e)

    def keep(self):
        while not self.stopped.isSet():
            self.keeprunning = True
            time.sleep(60)
            self.state.pongcheck = True
            self.command("PING", self.cfg.server)
            time.sleep(10.0)
            if self.state.pongcheck:
                self.keeprunning = False
                try:
                    self.restart()
                except ConnectionResetError:
                    continue
                break

    def logon(self, server, nick):
        self.raw("NICK %s" % nick)
        self.raw("USER %s %s %s :%s" % (self.cfg.username or "ob", server, server, self.cfg.realname or "python3 object library"))

    def parsing(self, txt):
        rawstr = str(txt)
        rawstr = rawstr.replace("\u0001", "")
        rawstr = rawstr.replace("\001", "")
        o = Event()
        o.rawstr = rawstr
        o.orig = Object.__dorepr__(self)
        o.command = ""
        o.arguments = []
        arguments = rawstr.split()
        if arguments:
            o.origin = arguments[0]
        else:
            o.origin = self.cfg.server
        if o.origin.startswith(":"):
            o.origin = o.origin[1:]
            if len(arguments) > 1:
                o.command = arguments[1]
                o.type = o.command
            if len(arguments) > 2:
                txtlist = []
                adding = False
                for arg in arguments[2:]:
                    if arg.count(":") <= 1 and arg.startswith(":"):
                        adding = True
                        txtlist.append(arg[1:])
                        continue
                    if adding:
                        txtlist.append(arg)
                    else:
                        o.arguments.append(arg)
                o.txt = " ".join(txtlist)
        else:
            o.command = o.origin
            o.origin = self.cfg.server
        try:
            o.nick, o.origin = o.origin.split("!")
        except ValueError:
            o.nick = ""
        target = ""
        if o.arguments:
            target = o.arguments[0]
        if target.startswith("#"):
            o.channel = target
        else:
            o.channel = o.nick
        if not o.txt:
            o.txt = rawstr.split(":", 2)[-1]
        if not o.txt and len(arguments) == 1:
            o.txt = arguments[1]
        spl = o.txt.split()
        if len(spl) > 1:
            o.args = spl[1:]
        o.type = o.command
        return o

    def poll(self):
        self.connected.wait()
        if not self.buffer:
            self.some()
        if self.buffer:
            return self.buffer.pop(0)

    def raw(self, txt):
        txt = txt.rstrip()
        if not txt.endswith("\r\n"):
            txt += "\r\n"
        txt = txt[:512]
        txt += "\n"
        txt = bytes(txt, "utf-8")
        self.sock.send(txt)
        self.state.last = time.time()
        self.state.nrsend += 1

    def say(self, channel, txt):
        self.oput(channel, txt)

    def some(self):
        self.connected.wait()
        inbytes = self.sock.recv(512)
        txt = str(inbytes, "utf-8")
        if txt == "":
            raise ConnectionResetError
        self.state.lastline += txt
        splitted = self.state.lastline.split("\r\n")
        for s in splitted[:-1]:
            self.buffer.append(s)
        self.state.lastline = splitted[-1]

    def start(self):
        self.cfg.last()
        if self.cfg.channel not in self.channels:
            self.channels.append(self.cfg.channel)
        self.stopped.clear()
        self.connected.clear()
        self.joined.clear()
        self.sock = None
        self.doconnect(self.cfg.server,
                       self.cfg.nick,
                       int(self.cfg.port))
        self.connected.wait()
        Handler.start(self)
        Output.start(self)
        Bus.add(self)
        if not self.keeprunning:
            launch(self.keep)
        self.wait()

    def stop(self):
        self.stopped.set()
        try:
            self.sock.shutdown(2)
        except OSError:
            pass
        Handler.stop(self)
        Output.stop(self)

    def wait(self):
        self.joined.wait()

class DCC(Handler):

    def __init__(self):
        super().__init__()
        self.encoding = "utf-8"
        self.origin = ""
        self.sock = None
        self.speed = "fast"

    def raw(self, txt):
        self.sock.send(bytes("%s\n" % txt.rstrip(), self.encoding))

    def announce(self, txt):
        pass

    def connect(self, dccevent):
        dccevent.parse()
        arguments = dccevent.otxt.split()
        addr = arguments[3]
        port = int(arguments[4])
        if ':' in addr:
            self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((addr, port))
        except ConnectionRefusedError:
            return
        self.sock.setblocking(1)
        os.set_inheritable(self.sock.fileno(), os.O_RDWR)
        self.fd = self.sock.fileno()
        self.raw('Welcome %s' % dccevent.origin)
        self.origin = dccevent.origin
        self.start()

    def dosay(self, channel, txt):
        self.raw(txt)

    def event(self, txt):
        e = Event()
        e.type = "cmd"
        e.channel = self.origin
        e.origin = self.origin or "root@dcc"
        e.orig = Object.__dorepr__(self)
        e.txt = txt.rstrip()
        e.sock = self.sock
        return e

    def handle(self, e):
        k.dispatch(e)

    def poll(self):
        return str(self.sock.recv(512), "utf8")

class User(Object):

    def __init__(self, val=None):
        super().__init__()
        self.user = ""
        self.perms = []
        if val:
            self.update(val)

class Users(Object):

    userhosts = Object()

    def allowed(self, origin, perm):
        perm = perm.upper()
        origin = getattr(self.userhosts, origin, origin)
        user = self.get_user(origin)
        if user:
            if perm in user.perms:
                return True
        return False

    def delete(self, origin, perm):
        for user in self.get_users(origin):
            try:
                user.perms.remove(perm)
                user.save()
                return True
            except ValueError:
                pass

    def get_users(self, origin=""):
        db = Db()
        s = {"user": origin}
        return db.find("om.irc.User", s)

    def get_user(self, origin):
        u = list(self.get_users(origin))
        if u:
            return u[-1][-1]

    def perm(self, origin, permission):
        user = self.get_user(origin)
        if not user:
            raise NoUserError(origin)
        if permission.upper() not in user.perms:
            user.perms.append(permission.upper())
            user.save()
        return user

def ERROR(clt, obj):
    clt.state.nrerror += 1
    clt.state.error = obj.error

def KILL(clt, obj):
    pass

def LOG(clt, obj):
    pass

def NOTICE(clt, obj):
    if obj.txt.startswith("VERSION"):
        txt = "\001VERSION %s %s - %s\001" % (clt.cfg.name.upper(), clt.cfg.version or 1, clt.cfg.username or "ob")
        clt.command("NOTICE", obj.channel, txt)

def PRIVMSG(clt, obj):
    if obj.txt.startswith("DCC CHAT"):
        if clt.cfg.users and not clt.users.allowed(obj.origin, "USER"):
            return
        try:
            dcc = DCC()
            launch(dcc.connect, obj)
            return
        except ConnectionError as ex:
            return
    if obj.txt:
        if obj.txt[0] in [clt.cfg.cc, "!"]:
            obj.txt = obj.txt[1:]
        elif obj.txt.startswith("%s:" % clt.cfg.nick):
            obj.txt = obj.txt[len(clt.cfg.nick)+1:]
        if clt.cfg.users and not clt.users.allowed(obj.origin, "USER"):
            return
        obj.type = "cmd"
        k.dispatch(obj)

def QUIT(clt, obj):
    if obj.orig and obj.orig in clt.zelf:
        clt.reconnect()

def cfg(event):
    c = Cfg()
    c.last()
    event.sets.delkeys(["p", "m"])
    if not event.sets:
        return event.reply(fmt(c, skip=["username", "realname"]))
    c.edit(event.sets)
    c.save()
    event.reply("ok")

def dlt(event):
    if not event.args:
        event.reply("dlt <username>")
        return
    db = Db()
    selector = {"user": event.args[0]}
    for fn, o in db.find("omirc.User", selector):
        o._deleted = True
        o.save()
        event.reply("ok")
        break

def met(event):
    if not event.args:
        event.reply("met <userhost>")
        return
    user = User()
    user.user = event.rest
    user.perms = ["USER"]
    user.save()
    event.reply("ok")

def mre(event):
    if event.channel is None:
        event.reply("channel is not set.")
        return
    if event.channel not in Output.cache:
        event.reply("no output in %s cache." % event.channel)
        return
    for txt in range(3):
        txt = Output.cache[event.channel].pop(0)
        if txt:
            event.say(txt)
    event.reply("(+%s more)" % Output.size(event.channel))
