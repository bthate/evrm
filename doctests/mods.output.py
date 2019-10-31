# mods/output.py
#
#

"""
    commands that output data.

    cmnds shows the available commands:

    >>> e = bot.cmnd("cmnds")
    alias,announce,begin,bot,cfg,chop,cmnds,deleted,dump,edit,end,fetcher,find,first,fleet,init,last,lijk,lijken,log,loud,mbox,meet,modules,permission,pid,prefix,ps,reboot,reload,restore,rm,rss,shop,shutdown,silent,start,stats,stop,timer,today,todo,tomorrow,uptime,user,version,w,week,whoami,wisdom,yesterday

    modules shows the available modules.

    >>> e = bot.cmnd("modules")
    {
        "_ready": "<threading.Event object at ...>"
    }

    announce announces on all channels of all connected bots

    >>> e = bot.cmnd("announce yo!")
    yo!

    fleet show all botids

    >>> e = bot.cmnd("fleet")
    TestBot.localhost

    bot shows the json of the bot the bot commands is typed on.

    >>> e = bot.cmnd("bot")
    {
        "_connected": {
            "_ready": "<threading.Event object at ...>",
            "_thrs": []
        },
        "_handlers": {},
        "_poll": "<select.epoll object at ...>",
        "_queue": "<queue.Queue object at ...>",
        "_resume": {},
        "_running": true,
        "_starttime": ...,
        "_status": "running",
        "_tasks": [],
        "_thrs": [
            "<Task(TestBot.schedule, started daemon ...)>",
            "<Task(TestBot.engine, started daemon ...)>"
        ],
        "cfg": {
            "cfg": "input",
            "owner": "root@shell",
            "prefix": "cfg",
            "server": "localhost",
            "silent": ""
        },
        "channels": [],
        "silent": false
    }

    the cfg command shows the last saved config of specific types

    >>> e = bot.cmnd("cfg")
    {
        "all": false,
        "args": [],
        "background": false,
        "cfg": "main",
        "colors": false,
        "debug": false,
        "default": [
            "aliases",
            "config"
        ],
        "exclude": "test",
        "init": "",
        "loglevel": "error",
        "modules": "",
        "name": "MADS",
        "nowait": true,
        "onerror": false,
        "openfire": false,
        "owner": "user@bot",
        "packages": [
            "mads",
            "mods",
            "muds"
        ],
        "path": false,
        "port": "10102",
        "prefix": "cfg",
        "reboot": false,
        "resume": false,
        "scan": false,
        "server": "main@server",
        "services": false,
        "shell": false,
        "skip": "",
        "verbose": true,
        "workdir": "/home/bart/.mads"
    }

"""
