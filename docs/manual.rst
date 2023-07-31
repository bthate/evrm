.. _manual:


.. raw:: html

    <br>


.. title:: Manual


.. raw:: html

    <center>

manual
######


.. raw:: html

    </center>


**NAME**

 | EVRM - 69389/12


**SYNOPSIS**

 ::

  evrm <cmd> [key=val] 
  evrm <cmd> [key==val]
  evrm [-c] [-d] [-v]


**DESCRIPTION**


 ``EVRM`` is a python3 IRC bot is intended to be programmable  in a
 static, only code, no popen, no user imports and no reading modules from
 a directory, way. It can show genocide and suicide stats of king netherlands
 his genocide into a IRC channel, display rss feeds and log simple text
 messages, source is `here <source.html>`_.



**INSTALL**

 with sudo::

  $ python3 -m pip install evrm

 as user::

  $ pipx install evrm

 or download the tar, see::

  https://pypi.org/project/evrm


**USAGE**


 list of commands::

    $ evrm cmd
    cmd,err,flt,sts,thr,upt

 start a console::

    $ evrm -c
    >

 start additional modules::

    $ evrm mod=<mod1,mod2> -c
    >

 list of modules::

    $ evrm mod
    cmd,err,flt,fnd,irc,log,mdl,mod,
    req, rss,slg,sts,tdo,thr,upt,ver

 to start irc, add mod=irc when
 starting::

     $ evrm mod=irc -c

 to start rss, also add mod=rss
 when starting::

     $ evrm mod=irc,rss -c

 start as daemon::

    $ evrm mod=irc,rss -d
    $ 


**CONFIGURATION**


 *irc*

 ::

    $ evrm cfg server=<server>
    $ evrm cfg channel=<channel>
    $ evrm cfg nick=<nick>

 *sasl*

 ::

    $ evrm pwd <nsvnick> <nspass>
    $ evrm cfg password=<frompwd>

 *rss*

 ::

    $ evrm rss <url>
    $ evrm dpl <url> <item1,item2>
    $ evrm rem <url>
    $ evrme nme <url< <name>


**COMMANDS**


 ::

    cmd - commands
    cfg - irc configuration
    dlt - remove a user
    dpl - sets display items
    ftc - runs a fetching batch
    fnd - find objects 
    flt - instances registered
    log - log some text
    mdl - genocide model
    met - add a user
    mre - displays cached output
    nck - changes nick on irc
    now - genocide stats
    pwd - sasl nickserv name/pass
    rem - removes a rss feed
    req - reconsider
    rss - add a feed
    slg - slogan
    thr - show the running threads
    tpc - genocide stats into topic


**FILES**

 ::

    ~/.local/bin/evrm
    ~/.local/pipx/venvs/evrm/
    /usr/local/bin/evrm
    /usr/local/share/doc/evrm


**AUTHOR**


 ::
 
    Bart Thate <bthate@dds.nl>


**COPYRIGHT**

 ::

    EVRM is Public Domain.
