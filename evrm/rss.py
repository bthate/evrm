# This file is placed in the Public Domain.

import ob
import re
import threading
import urllib

from ob import Bus, Repeater, kernel

from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus, urlencode
from urllib.request import Request, urlopen

def __dir__():
    return ("Cfg", "Feed", "Rss", "Seen", "Fetcher", "dpl", "ftc", "init", "rem", "rss")

def init(k):
    f = Fetcher()
    ob.launch(f.start)
    return f

k = kernel()

class Cfg(ob.Default):

    def __init__(self):
        super().__init__()
        self.dosave = False
        self.display_list = "title,link"
        self.tinyurl = False

class Feed(ob.Default):

    pass

class Rss(ob.Object):

    def __init__(self):
        super().__init__()
        self.rss = ""

class Seen(ob.Object):

    def __init__(self):
        super().__init__()
        self.urls = []

class Fetcher(ob.Object):

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
        for o in reversed(list(getfeed(feed.rss))):
            f = Feed(dict(o))
            f.update(feed)
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
            f.save()
        if objs:
            Fetcher.seen.save()
        for o in objs:
            txt = self.display(o)
            Bus.announce(txt)
        return counter

    def run(self):
        db = ob.Db()
        thrs = []
        for fn, o in db.all("om.rss.Rss"):
            thrs.append(ob.launch(self.fetch, o))
        return thrs

    def start(self, repeat=True):
        Fetcher.cfg.last()
        Fetcher.seen.last()
        if repeat:
            repeater = Repeater(300.0, self.run)
            repeater.start()

    def stop(self):
        self.seen.save()

def getfeed(url):
    try:
        import feedparser
    except ModuleNotFoundError:
        return [ob.Object(), ob.Object()]
    try:
        result = geturl(url)
    except (ValueError, HTTPError, URLError) as ex:
        return [ob.Object(), ob.Object()]
    if not result:
        return [ob.Object(), ob.Object()]
    else:
        result = feedparser.parse(result.data)
        if result and "entries" in result:
            for entry in result["entries"]:
                yield entry

def gettinyurl(url):
    if k.cfg.debug:
        return []
    postarray = [
        ('submit', 'submit'),
        ('url', url),
        ]
    postdata = urlencode(postarray, quote_via=quote_plus)
    req = Request('http://tinyurl.com/create.php', data=bytes(postdata, "UTF-8"))
    req.add_header('User-agent', useragent(url))
    for txt in urlopen(req).readlines():
        line = txt.decode("UTF-8").strip()
        i = re.search('data-clipboard-text="(.*?)"', line, re.M)
        if i:
            return i.groups()
    return []

def geturl(url):
    if k.cfg.debug:
        return
    url = urllib.parse.urlunparse(urllib.parse.urlparse(url))
    req = urllib.request.Request(url)
    req.add_header('User-agent', useragent("BOTLIB"))
    response = urllib.request.urlopen(req)
    response.data = response.read()
    return response

def striphtml(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def unescape(text):
    import html.parser
    txt = re.sub(r"\s+", " ", text)
    return html.unescape(txt)

def useragent(txt):
    return 'Mozilla/5.0 (X11; Linux x86_64) ' + txt

def dpl(event):
    if len(event.args) < 2:
        event.reply("dpl <stringinurl> <item1,item2>")
        return
    db = ob.Db()
    setter = {"display_list": event.args[1]}
    fn, o = db.lastmatch("om.rss.Rss", {"rss": event.args[0]})
    if o:
        o.edit(setter)
        o.save()
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
    event.reply("no result")

def rem(event):
    if not event.args:
        event.reply("rem <stringinurl>")
        return
    db = ob.Db()
    selector = {"rss": event.args[0]}
    nr = 0
    got = []
    for fn, o in db.find("om.rss.Rss", selector):
        nr += 1
        o._deleted = True
        got.append(o)
    for o in got:
        o.save()
    event.reply("ok")

def rss(event):
    if not event.args:
        event.reply("rss <url>")
        return
    db = ob.Db()
    url = event.args[0]
    res = list(db.find("om.rss.Rss", {"rss": url}))
    if res:
        return
    o = Rss()
    o.rss = event.args[0]
    o.save()
    event.reply("ok")
