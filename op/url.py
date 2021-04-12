# This file is placed in the Public Domain.

"urls"

import re
import urllib

from urllib.parse import quote_plus, urlencode
from urllib.request import Request, urlopen

debug = False

def gettinyurl(url):
    if debug:
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
    if debug:
        return
    url = urllib.parse.urlunparse(urllib.parse.urlparse(url))
    req = urllib.request.Request(url)
    req.add_header('User-agent', useragent(url))
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
