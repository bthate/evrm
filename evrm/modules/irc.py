# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R,W0401,W0622,W0613
# flake8: noqa=C901


"internet relay chat"


import base64
import os
import queue
import random
import socket
import ssl
import time
import textwrap
import threading
import _thread


from ..bus     import Bus
from ..command import Command
from ..error   import Error
from ..event   import Event
from ..object  import Default, Object
from ..object  import edit, keys, printable, update
from ..persist import Persist, find, fntime, last, write
from ..reactor import Reactor
from ..thread  import launch
from ..utils   import laps


NAME = __file__.split(os.sep)[-3]


saylock = _thread.allocate_lock()


def start():
    irc = IRC()
    irc.start()
    irc.events.joined.wait()
    return irc


def stop():
    for bot in Bus.objs:
        if "IRC" in str(type(bot)):
            bot.stop()


class NoUser(Exception):

    pass


class Config(Object):

    channel = f'#{NAME}'
    control = '!'
    edited = time.time()
    nick = NAME
    nocommands = False
    password = ''
    port = 6667
    realname = NAME
    sasl = False
    server = 'localhost'
    servermodes = ''
    sleep = 60
    username = NAME
    users = False
    verbose = False

    def __init__(self):
        Object.__init__(self)
        self.channel = Config.channel
        self.nick = Config.nick
        self.port = Config.port
        self.realname = Config.realname
        self.server = Config.server
        self.username = Config.username

    def __edited__(self):
        return Config.edited

    def __size__(self):
        return len(Config)


Persist.add(Config)


class TextWrap(textwrap.TextWrapper):

    def __init__(self):
        super().__init__()
        self.break_long_words = False
        self.drop_whitespace = True
        self.fix_sentence_endings = True
        self.replace_whitespace = True
        self.tabsize = 4
        self.width = 450


class Output(Object):

    cache = Object()

    def __init__(self):
        Object.__init__(self)
        self.oqueue = queue.Queue()
        self.dostop = threading.Event()

    def dosay(self, channel, txt):
        raise NotImplementedError

    def extend(self, channel, txtlist):
        if channel not in self.cache:
            setattr(self.cache, channel, [])
        cache = getattr(self.cache, channel, None)
        cache.extend(txtlist)

    def gettxt(self, channel):
        txt = None
        try:
            cache = getattr(self.cache, channel, None)
            txt = cache.pop(0)
        except (KeyError, IndexError):
            pass
        return txt

    def oput(self, channel, txt):
        if channel not in self.cache:
            setattr(self.cache, channel, [])
        self.oqueue.put_nowait((channel, txt))

    def output(self):
        while not self.dostop.is_set():
            (channel, txt) = self.oqueue.get()
            if channel is None and txt is None:
                break
            if self.dostop.is_set():
                break
            wrapper = TextWrap()
            try:
                txtlist = wrapper.wrap(txt)
            except AttributeError:
                continue
            if len(txtlist) > 3:
                self.extend(channel, txtlist)
                length = len(txtlist)
                self.dosay(
                           channel,
                           f"use !mre to show more (+{length})"
                          )
                continue
            _nr = -1
            for txt in txtlist:
                _nr += 1
                self.dosay(channel, txt)

    def size(self, chan):
        if chan in self.cache:
            return len(getattr(self.cache, chan, []))
        return 0

    def start(self):
        self.dostop.clear()
        launch(self.output)
        return self

    def stop(self):
        self.dostop.set()
        self.oqueue.put_nowait((None, None))


class IRC(Reactor, Output):

    def __init__(self):
        Reactor.__init__(self)
        Output.__init__(self)
        self.buffer = []
        self.cfg = Config()
        self.events = Default()
        self.events.authed = threading.Event()
        self.events.connected = threading.Event()
        self.events.joined = threading.Event()
        self.channels = []
        self.sock = None
        self.state = Default()
        self.state.keeprunning = False
        self.state.nrconnect = 0
        self.state.nrsend = 0
        self.zelf = ''
        self.register('903', cb_h903)
        self.register('904', cb_h903)
        self.register('AUTHENTICATE', cb_auth)
        self.register('CAP', cb_cap)
        self.register('ERROR', cb_error)
        self.register('LOG', cb_log)
        self.register('NOTICE', cb_notice)
        self.register('PRIVMSG', cb_privmsg)
        self.register('QUIT', cb_quit)
        Bus.add(self)

    def announce(self, txt):
        for channel in self.channels:
            self.say(channel, txt)

    def command(self, cmd, *args):
        with saylock:
            if not args:
                self.raw(cmd)
            elif len(args) == 1:
                self.raw(f'{cmd.upper()} {args[0]}')
            elif len(args) == 2:
                txt = ' '.join(args[1:])
                self.raw(f'{cmd.upper()} {args[0]} :{txt}')
            elif len(args) >= 3:
                txt = ' '.join(args[2:])
                self.raw("{cmd.upper()} {args[0]} {args[1]} :{txt}")
            if (time.time() - self.state.last) < 5.0:
                time.sleep(5.0)
            self.state.last = time.time()

    def connect(self, server, port=6667):
        self.state.nrconnect += 1
        self.events.connected.clear()
        Error.debug(f"connecting to {server}:{port}")
        if self.cfg.password:
            Error.debug("using SASL")
            self.cfg.sasl = True
            self.cfg.port = "6697"
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
            ctx.check_hostname = False
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock = ctx.wrap_socket(sock)
            self.sock.connect((server, port))
            time.sleep(1.0)
            self.command('CAP LS 302')
        else:
            addr = socket.getaddrinfo(server, port, socket.AF_INET)[-1][-1]
            self.sock = socket.create_connection(addr)
            self.events.authed.set()
        if self.sock:
            os.set_inheritable(self.sock.fileno(), os.O_RDWR)
            self.sock.setblocking(True)
            self.sock.settimeout(180.0)
            self.events.connected.set()
            return True
        return False

    def direct(self, txt):
        Error.debug(txt)
        self.sock.send(bytes(txt.rstrip()+'\r\n', 'utf-8'))

    def disconnect(self):
        try:
            self.sock.shutdown(2)
        except (
                ssl.SSLError,
                OSError,
                BrokenPipeError
               ) as ex:
            Error.errors.append(ex)

    def doconnect(self, server, nck, port=6667):
        while 1:
            try:
                if self.connect(server, port):
                    break
            except (
                    ssl.SSLError,
                    OSError,
                    ConnectionResetError
                   ) as ex:
                self.state.errors = str(ex)
                Error.debug(str(ex))
            Error.debug(f"sleeping {self.cfg.sleep} seconds")
            time.sleep(self.cfg.sleep)
        #self.logon(server, nck)

    def dosay(self, channel, txt):
        self.events.joined.wait()
        #txt = str(txt).replace('\n', '')
        #txt = txt.replace('  ', ' ')
        self.command('PRIVMSG', channel, txt)

    def event(self, txt):
        evt = self.parsing(txt)
        cmd = evt.command
        if cmd == "020":
            self.logon(self.cfg.server, self.cfg.nick)
        if cmd == 'PING':
            self.state.pongcheck = True
            self.command('PONG', evt.txt or '')
        elif cmd == 'PONG':
            self.state.pongcheck = False
        if cmd == '001':
            self.state.needconnect = False
            if self.cfg.servermodes:
                self.command(f'MODE {self.cfg.nick} {self.cfg.servermodes}')
            self.zelf = evt.args[-1]
        elif cmd == "376":
            self.joinall()
        elif cmd == '002':
            self.state.host = evt.args[2][:-1]
        elif cmd == '366':
            self.state.errors = []
            self.events.joined.set()
        elif cmd == '433':
            self.state.errors = txt
            nck = self.cfg.nick + '_' + str(random.randint(1, 10))
            self.command('NICK', nck)
        return evt

    def joinall(self):
        for channel in self.channels:
            self.command('JOIN', channel)

    def keep(self):
        while 1:
            self.events.connected.wait()
            self.events.authed.wait()
            self.state.keeprunning = True
            time.sleep(self.cfg.sleep)
            self.state.pongcheck = True
            self.command('PING', self.cfg.server)
            if self.state.pongcheck:
                Error.debug("failed pongcheck, restarting")
                self.state.pongcheck = False
                self.state.keeprunning = False
                self.events.connected.clear()
                self.stop()
                start()
                break

    def logon(self, server, nck):
        self.events.connected.wait()
        self.events.authed.wait()
        nck = self.cfg.username
        self.direct(f'NICK {nck}')
        self.direct(f'USER {nck} {server} {server} {nck}')

    def parsing(self, txt):
        rawstr = str(txt)
        rawstr = rawstr.replace('\u0001', '')
        rawstr = rawstr.replace('\001', '')
        Error.debug(txt)
        obj = Event()
        obj.rawstr = rawstr
        obj.command = ''
        obj.arguments = []
        arguments = rawstr.split()
        if arguments:
            obj.origin = arguments[0]
        else:
            obj.origin = self.cfg.server
        if obj.origin.startswith(':'):
            obj.origin = obj.origin[1:]
            if len(arguments) > 1:
                obj.command = arguments[1]
                obj.type = obj.command
            if len(arguments) > 2:
                txtlist = []
                adding = False
                for arg in arguments[2:]:
                    if arg.count(':') <= 1 and arg.startswith(':'):
                        adding = True
                        txtlist.append(arg[1:])
                        continue
                    if adding:
                        txtlist.append(arg)
                    else:
                        obj.arguments.append(arg)
                obj.txt = ' '.join(txtlist)
        else:
            obj.command = obj.origin
            obj.origin = self.cfg.server
        try:
            obj.nick, obj.origin = obj.origin.split('!')
        except ValueError:
            obj.nick = ''
        target = ''
        if obj.arguments:
            target = obj.arguments[0]
        if target.startswith('#'):
            obj.channel = target
        else:
            obj.channel = obj.nick
        if not obj.txt:
            obj.txt = rawstr.split(':', 2)[-1]
        if not obj.txt and len(arguments) == 1:
            obj.txt = arguments[1]
        spl = obj.txt.split()
        if len(spl) > 1:
            obj.args = spl[1:]
        if obj.args:
            obj.rest = " ".join(obj.args)
        obj.orig = repr(self)
        obj.txt = obj.txt.strip()
        obj.type = obj.command
        return obj

    def poll(self):
        self.events.connected.wait()
        if not self.buffer:
            try:
                self.some()
            except BlockingIOError as ex:
                time.sleep(1.0)
                return self.event(str(ex))
            except (
                    OSError,
                    socket.timeout,
                    ssl.SSLError,
                    ssl.SSLZeroReturnError,
                    ConnectionResetError,
                    BrokenPipeError
                   ) as ex:
                Error.errors.append(ex)
                self.stop()
                Error.debug("handler stopped")
                return self.event(str(ex))
        try:
            txt = self.buffer.pop(0)
        except IndexError:
            txt = ""
        return self.event(txt)

    def raw(self, txt):
        txt = txt.rstrip()
        Error.debug(txt)
        if not txt.endswith('\r\n'):
            txt += '\r\n'
        txt = txt[:512]
        txt += '\n'
        txt = bytes(txt, 'utf-8')
        if self.sock:
            try:
                self.sock.send(txt)
            except (
                    OSError,
                    ssl.SSLError,
                    ssl.SSLZeroReturnError,
                    ConnectionResetError,
                    BrokenPipeError
                   ) as ex:
                Error.errors.append(ex)
                self.stop()
                return
        self.state.last = time.time()
        self.state.nrsend += 1

    def reconnect(self):
        Error.debug(f"reconnecting to {self.cfg.server}")
        try:
            self.disconnect()
        except (ssl.SSLError, OSError):
            pass
        self.events.connected.clear()
        self.events.joined.clear()
        self.doconnect(self.cfg.server, self.cfg.nick, int(self.cfg.port))

    def say(self, channel, txt):
        self.oput(channel, txt)

    def some(self):
        self.events.connected.wait()
        if not self.sock:
            return
        inbytes = self.sock.recv(512)
        txt = str(inbytes, 'utf-8')
        if txt == '':
            raise ConnectionResetError
        self.state.lastline += txt
        splitted = self.state.lastline.split('\r\n')
        for line in splitted[:-1]:
            self.buffer.append(line)
        self.state.lastline = splitted[-1]

    def start(self):
        last(self.cfg)
        if self.cfg.channel not in self.channels:
            self.channels.append(self.cfg.channel)
        self.events.connected.clear()
        self.events.joined.clear()
        Reactor.start(self)
        Output.start(self)
        launch(
               self.doconnect,
               self.cfg.server or "localhost",
               self.cfg.nick,
               int(self.cfg.port or '6667')
              )
        if not self.state.keeprunning:
            launch(self.keep)

    def stop(self):
        Bus.remove(self)
        Reactor.stop(self)
        Output.stop(self)
        self.disconnect()


class User(Object):

    def __init__(self, val=None):
        Object.__init__(self)
        self.user = ''
        self.perms = []
        if val:
            update(self, val)

    def isok(self):
        return True

    def isthere(self):
        return True


Persist.add(User)


class Users(Object):

    @staticmethod
    def allowed(origin, perm):
        perm = perm.upper()
        user = Users.get_user(origin)
        val = False
        if user and perm in user.perms:
            val = True
        return val

    @staticmethod
    def delete(origin, perm):
        res = False
        for user in Users.get_users(origin):
            try:
                user.perms.remove(perm)
                write(user)
                res = True
            except ValueError:
                pass
        return res

    @staticmethod
    def get_users(origin=''):
        selector = {'user': origin}
        return find('user', selector)

    @staticmethod
    def get_user(origin):
        users = list(Users.get_users(origin))
        res = None
        if len(users) > 0:
            res = users[-1]
        return res

    @staticmethod
    def perm(origin, permission):
        user = Users.get_user(origin)
        if not user:
            raise NoUser(origin)
        if permission.upper() not in user.perms:
            user.perms.append(permission.upper())
            write(user)
        return user


# CALLBACKS


def cb_auth(evt):
    bot = Bus.byorig(evt.orig)
    assert bot.cfg.password
    bot.command(f'AUTHENTICATE {bot.cfg.password}')


def cb_cap(evt):
    bot = Bus.byorig(evt.orig)
    if bot.cfg.password and 'ACK' in evt.arguments:
        bot.command('AUTHENTICATE PLAIN')
    else:
        bot.command('CAP REQ :sasl')


def cb_command(evt):
    Command.handle(evt)


def cb_error(evt):
    bot = Bus.byorig(evt.orig)
    bot.state.nrerror += 1
    bot.state.errors.append(evt.txt)
    Error.debug(evt.txt)


def cb_h903(evt):
    assert evt
    bot = Bus.byorig(evt.orig)
    bot.command('CAP END')
    bot.events.authed.set()


def cb_h904(evt):
    assert evt
    bot = Bus.byorig(evt.orig)
    bot.command('CAP END')
    bot.events.authed.set()


def cb_kill(evt):
    pass


def cb_log(evt):
    pass


def cb_001(evt):
    bot = Bus.byorig(evt.orig)
    bot.logon()

def cb_notice(evt):
    bot = Bus.byorig(evt.orig)
    if evt.txt.startswith('VERSION'):
        txt = f'\001VERSION {NAME.upper()} 140 - {bot.cfg.username}\001'
        bot.command('NOTICE', evt.channel, txt)


def cb_privmsg(evt):
    bot = Bus.byorig(evt.orig)
    if bot.cfg.nocommands:
        return
    if evt.txt:
        if evt.txt[0] in ['!',]:
            evt.txt = evt.txt[1:]
        elif evt.txt.startswith(f'{bot.cfg.nick}:'):
            evt.txt = evt.txt[len(bot.cfg.nick)+1:]
        else:
            return
        if evt.txt:
            evt.txt = evt.txt[0].lower() + evt.txt[1:]
        if bot.cfg.users and not Users.allowed(evt.origin, 'USER'):
            return
        Error.debug(f"command from {evt.origin}: {evt.txt}")
        Command.handle(evt)


def cb_quit(evt):
    bot = Bus.byorig(evt.orig)
    Error.debug(f"quit from {bot.cfg.server}")
    if evt.orig and evt.orig in bot.zelf:
        bot.stop()


# COMMANDS


def cfg(event):
    config = Config()
    last(config)
    if not event.sets:
        event.reply(
                    printable(
                        config,
                        keys(config),
                        skip='control,password,realname,sleep,username'
                       )
                   )
    else:
        edit(config, event.sets)
        write(config)
        event.reply('ok')


def dlt(event):
    if not event.args:
        event.reply('dlt <username>')
        return
    selector = {'user': event.args[0]}
    for obj in find('user', selector):
        obj.__deleted__ = True
        write(obj)
        event.reply('ok')
        break


def met(event):
    if not event.args:
        nmr = 0
        for obj in find('user'):
            lap = laps(time.time() - fntime(obj.__fnm__))
            event.reply(f'{nmr} {obj.user} {obj.perms} {lap}s')
            nmr += 1
        if not nmr:
            event.reply('no user')
        return
    user = User()
    user.user = event.rest
    user.perms = ['USER']
    write(user)
    event.reply('ok')


def mre(event):
    if not event.channel:
        event.reply('channel is not set.')
        return
    bot = event.bot()
    if 'cache' not in dir(bot):
        event.reply('bot is missing cache')
        return
    if event.channel not in bot.cache:
        event.reply(f'no output in {event.channel} cache.')
        return
    for _x in range(3):
        txt = bot.gettxt(event.channel)
        if txt:
            bot.say(event.channel, txt)
    size = bot.size(event.channel)
    event.reply(f'{size} more in cache')


def pwd(event):
    if len(event.args) != 2:
        event.reply('pwd <nick> <password>')
        return
    arg1 = event.args[0]
    arg2 = event.args[1]
    txt = f'\x00{arg1}\x00{arg2}'
    enc = txt.encode('ascii')
    base = base64.b64encode(enc)
    dcd = base.decode('ascii')
    event.reply(dcd)
