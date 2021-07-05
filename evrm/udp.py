# This file is placed in the Public Domain.

import ob
import socket
import time

def __dir__():
    return ("Cfg", "UDP", "init", "toudp")

def init(k):
    u = UDP()
    u.start()
    return u

class Cfg(ob.Default):

    host = "localhost"
    port = 5500

    def __init__(self):
        super().__init__()
        self.host = Cfg.host
        self.port = Cfg.port

class UDP(ob.Object):

    def __init__(self):
        super().__init__()
        self.stopped = False
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self._sock.setblocking(1)
        self._starttime = time.time()
        self.cfg = Cfg()

    def output(self, txt, addr):
        ob.hdl.Bus.announce(txt.replace("\00", ""))

    def server(self):
        try:
            self._sock.bind((self.cfg.host, self.cfg.port))
        except (socket.gaierror, OSError):
            return
        while not self.stopped:
            (txt, addr) = self._sock.recvfrom(64000)
            if self.stopped:
                break
            data = str(txt.rstrip(), "utf-8")
            if not data:
                break
            self.output(data, addr)

    def start(self):
        self.cfg.last()
        ob.launch(self.server)

    def stop(self):
        self.stopped = True
        self._sock.settimeout(0.01)
        self._sock.sendto(bytes("exit", "utf-8"), (self.cfg.host, self.cfg.port))

def toudp(host, port, txt):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(bytes(txt.strip(), "utf-8"), (host, port))
