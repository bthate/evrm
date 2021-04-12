# This file is placed in the Public Domain.

"feeds"

from botl.bus import Bus
from botl.dbs import find
from botl.edt import edit
from botl.clk import Repeater
from botl.dbs import all, find, last, lastmatch
from botl.obj import Cfg, Default, Object, save
from botl.thr import launch
from botl.url import geturl, striphtml, unescape
from botl.zzz import html, re, threading, urllib

from urllib.error import HTTPError, URLError

try:
    import feedparser
    gotparser = True
except ModuleNotFoundError:
    gotparser = False

def init(hdl):
    f = Fetcher()
    launch(f.start)
    return f

class Cfg(Cfg):

    def __init__(self):
        super().__init__()
        self.dosave = False
        self.display_list = "title,link"
        self.tinyurl = False

class Feed(Default):

    pass

class Rss(Object):

    def __init__(self):
        super().__init__()
        self.rss = ""

class Seen(Object):

    def __init__(self):
        super().__init__()
        self.urls = []

class Fetcher(Object):

    cfg = Cfg()
    seen = Seen()

    def __init__(self):
        super().__init__()
        self.connected = threading.Event()

    def display(self, o):
        result = ""
        dl = []
        try:
            dl = o.display_list.split(",")
        except AttributeError:
            pass
        if not dl:
            dl = self.cfg.display_list.split(",")
        if not dl or not dl[0]:
            dl = ["title", "link"]
        for key in dl:
            if not key:
                continue
            data = o.get(key, None)
            if not data:
                continue
            data = data.replace("\n", " ")
            data = striphtml(data.rstrip())
            data = unescape(data)
            result += data.rstrip()
            result += " - "
        return result[:-2].rstrip()

    def fetch(self, feed):
        counter = 0
        objs = []
        if not feed.rss:
            return 0
        for o in reversed(list(getfeed(feed.rss))):
            if not o:
                continue
            f = Feed()
            f.update(feed)
            f.update(dict(o))
            u = urllib.parse.urlparse(f.link)
            if u.path and not u.path == "/":
                url = "%s://%s/%s" % (u.scheme, u.netloc, u.path)
            else:
                url = f.link
            if url in Fetcher.seen.urls:
                continue
            Fetcher.seen.urls.append(url)
            counter += 1
            objs.append(f)
            if self.cfg.dosave:
                save(f)
        if objs:
            save(Fetcher.seen)
        for o in objs:
            txt = self.display(o)
            Bus.announce(txt)
        return counter

    def run(self):
        thrs = []
        for fn, o in all("botd.rss.Rss"):
            thrs.append(launch(self.fetch, o))
        return thrs

    def start(self, repeat=True):
        last(Fetcher.cfg)
        last(Fetcher.seen)
        if repeat:
            repeater = Repeater(300.0, self.run)
            repeater.start()

    def stop(self):
        save(self.seen)

def getfeed(url):
    got = False
    if gotparser:
        try:
            result = geturl(url)
            if not result:
                got = False
            else:
                result = feedparser.parse(result.data)
                if result and "entries" in result:
                    got = True
                    for entry in result["entries"]:
                        yield entry
        except (ValueError, HTTPError, URLError):
            pass
    if not got:
        return [Object(), Object()]

def dpl(event):
    if len(event.args) < 2:
        event.reply("dpl <stringinurl> <item1,item2>")
        return
    setter = {"display_list": event.args[1]}
    fn, o = lastmatch("botd.rss.Rss", {"rss": event.args[0]})
    if o:
        edit(o, setter)
        save(o)
        event.reply("ok")

def ftc(event):
    res = []
    thrs = []
    fetcher = Fetcher()
    fetcher.start(False)
    thrs = fetcher.run()
    for thr in thrs:
        res.append(thr.join() or 0)
    if res:
        event.reply("fetched %s" % ",".join([str(x) for x in res]))
        return

def rem(event):
    if not event.args:
        event.reply("rem <stringinurl>")
        return
    selector = {"rss": event.args[0]}
    nr = 0
    got = []
    for fn, o in find("botd.rss.Rss", selector):
        nr += 1
        o._deleted = True
        got.append(o)
    for o in got:
        save(o)
    event.reply("ok")

def rss(event):
    if not event.args:
        event.reply("rss <url>")
        return
    url = event.args[0]
    res = list(find("botd.rss.Rss", {"rss": url}))
    if res:
        return
    o = Rss()
    o.rss = event.args[0]
    save(o)
    event.reply("ok")
