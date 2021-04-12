# This file is placed in the Public Domain.

"bot"

__version__ = 36

from botl.bus import Bus
from botl.clt import Client
from botl.dbs import find, last
from botl.edt import edit
from botl.err import ENOUSER
from botl.evt import Event
from botl.obj import Cfg, Object, fmt, save
from botl.opt import Output
from botl.hdl import Handler, cmd
from botl.thr import launch
from botl.trc import exception
from botl.usr import Users
from botl.utl import cprint, locked
from botl.zzz import os, queue, socket, textwrap
from botl.zzz import time, threading, _thread

def init(hdl):
    i = IRC()
    i.addbus()
    i.start()
    return i

saylock = _thread.allocate_lock()

class Cfg(Cfg):


    def __init__(self, val=None):
        super().__init__()
        self.cc = "!"
        self.channel = "#botd"
        self.nick = "botd"
        self.port = 6667
        self.server = "localhost"
        self.realname = "24/7 channel daemon"
        self.username = "botd"
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

class IRC(Output, Client):

    def __init__(self):
        Client.__init__(self)
        Output.__init__(self)
        self.buffer = []
        self.cfg = Cfg()
        self.connected = threading.Event()
        self.channels = []
        self.sock = None
        self.joined = threading.Event()
        self.keeprunning = False
        self.outqueue = queue.Queue()
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
        self.register("cmd", cmd)
        self.register("ERROR", ERROR)
        self.register("LOG", LOG)
        self.register("NOTICE", NOTICE)
        self.register("PRIVMSG", PRIVMSG)
        self.register("QUIT", QUIT)

    def announce(self, txt):
        for channel in self.channels:
            self.say(channel, txt)

    def command(self, cmd, *args):
        self.connected.wait()
        if not args:
            self.raw(cmd)
            return
        if len(args) == 1:
            self.raw("%s %s" % (cmd.upper(), args[0]))
            return
        if len(args) == 2:
            self.raw("%s %s :%s" % (cmd.upper(), args[0], " ".join(args[1:])))
            return
        if len(args) >= 3:
            self.raw("%s %s %s :%s" % (cmd.upper(), args[0], args[1], " ".join(args[2:])))
            return

    def connect(self, server, port=6667):
        cprint("connect %s:%s" % (server, port))
        addr = socket.getaddrinfo(server, port, socket.AF_INET)[-1][-1]
        self.sock = socket.create_connection(addr)
        os.set_inheritable(self.fileno(), os.O_RDWR)
        self.sock.setblocking(True)
        self.sock.settimeout(180.0)
        self.connected.set()
        return True

    def doconnect(self, server, nick, port=6667):
        self.state.nrconnect = 0
        while not self.stopped:
            self.state.nrconnect += 1
            try:
                if self.connect(server, port):
                    break
            except (ConnectionResetError, OSError):
                pass
            time.sleep(10.0 * self.state.nrconnect)
        self.logon(server, nick)

    @locked(saylock)
    def dosay(self, channel, txt):
        wrapper = TextWrap()
        txt = str(txt).replace("\n", "")
        for t in wrapper.wrap(txt):
            if not t:
                continue
            self.command("PRIVMSG", channel, t)
            if (time.time() - self.state.last) < 4.0:
                time.sleep(4.0)
            self.state.last = time.time()

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

    def joinall(self):
        for channel in self.channels:
            self.command("JOIN", channel)

    def keep(self):
        while not self.stopped:
            self.keeprunning = True
            time.sleep(60)
            self.state.pongcheck = True
            self.command("PING", self.cfg.server)
            time.sleep(5.0)
            if self.state.pongcheck:
                self.keeprunning = False
                try:
                    self.reconnect()
                except ConnectionResetError:
                    continue
                break

    def logon(self, server, nick):
        self.raw("NICK %s" % nick)
        self.raw("USER %s %s %s :%s" % (self.cfg.username, server, server, self.cfg.realname))

    def parsing(self, txt):
        rawstr = str(txt)
        rawstr = rawstr.replace("\u0001", "")
        rawstr = rawstr.replace("\001", "")
        cprint(rawstr)
        o = Event()
        o.rawstr = rawstr
        o.orig = repr(self)
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
        cprint(txt.rstrip())
        txt = bytes(txt, "utf-8")
        self.sock.send(txt)
        self.state.last = time.time()
        self.state.nrsend += 1

    def reconnect(self):
        cprint("reconnect to %s" % self.cfg.server) 
        self.stop()
        time.sleep(5.0)
        self.stopped = False
        self.start()

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
        last(self.cfg)
        if self.cfg.channel not in self.channels:
            self.channels.append(self.cfg.channel)
        self.stopped = False
        self.connected.clear()
        self.joined.clear()
        self.sock = None
        self.doconnect(self.cfg.server, self.cfg.nick, int(self.cfg.port) or 6667)
        Client.start(self)
        Output.start(self)
        if not self.keeprunning:
            launch(self.keep)
        self.wait()

    def stop(self):
        self.stopped = True
        try:
            self.sock.shutdown(2)
        except OSError:
            pass
        Client.stop(self)
        Output.stop(self)
        
    def wait(self):
        self.joined.wait()

class DCC(Client):

    def __init__(self):
        super().__init__()
        self.encoding = "utf-8"
        self.origin = ""
        self.sock = None
        self.stopped = False
        self.register("cmd", cmd)

    def raw(self, txt):
        self.sock.send(bytes("%s\n" % txt.rstrip(), self.encoding))

    def announce(self, txt):
        pass

    def connect(self, dccevent):
        dccevent.parse()
        arguments = dccevent.old.txt.split()
        addr = arguments[3]
        port = int(arguments[4])
        if ':' in addr:
            self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((addr, port))
        except ConnectionRefusedError:
            self.connected.set()
            return
        self.sock.setblocking(1)
        os.set_inheritable(self.sock.fileno(), os.O_RDWR)
        self.fd = self.sock.fileno()
        self.raw('Welcome %s' % dccevent.origin)
        self.origin = dccevent.origin
        super().start()
        self.addbus()

    def dosay(self, channel, txt):
        self.raw(txt)

    def event(self, txt):
        e = Event()
        e.type = "cmd"
        e.channel = self.origin
        e.origin = self.origin or "root@dcc"
        e.orig = repr(self)
        e.txt = txt.rstrip()
        e.sock = self.sock
        #self.put(e)
        return e

    def poll(self):
        return str(self.sock.recv(512), "utf8")

def ERROR(hdl, obj):
    hdl.state.nrerror += 1
    hdl.state.error = obj.error

def KILL(hdl, obj):
    pass

def LOG(hdl, obj):
    pass
    
def NOTICE(hdl, obj):
    if obj.txt.startswith("VERSION"):
        txt = "\001VERSION %s %s - %s\001" % (hdl.cfg.name.upper(), hdl.cfg.version or __version__, hdl.cfg.username)
        hdl.command("NOTICE", obj.channel, txt)

def PRIVMSG(hdl, obj):
    if obj.txt.startswith("DCC CHAT"):
        if hdl.cfg.users and not hdl.users.allowed(obj.origin, "USER"):
            return
        try:
            dcc = DCC()
            launch(dcc.connect, obj)
            return
        except ConnectionError as ex:
            return
    if obj.txt:
        if obj.txt[0] in [hdl.cfg.cc, "!"]:
            obj.txt = obj.txt[1:]
        elif obj.txt.startswith("%s:" % hdl.cfg.nick):
            obj.txt = obj.txt[len(hdl.cfg.nick)+1:]
        if hdl.cfg.users and not hdl.users.allowed(obj.origin, "USER"):
            return
        obj.type = "cmd"
        hdl.put(obj)

def QUIT(hdl, obj):
    if obj.orig and obj.orig in hdl.zelf:
        hdl.reconnect()

def cfg(event):
    c = Cfg()
    last(c)
    if not event.sets:
        return event.reply(fmt(c, skip=["username", "realname"]))
    edit(c, event.sets)
    save(c)
    event.reply("ok")
