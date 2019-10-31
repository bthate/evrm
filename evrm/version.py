# evrm/version.py
#
#

from evrm import __version__, __txt__

def version(event):
    event.reply("EVRM #%s - %s" % (__version__, __txt__))
