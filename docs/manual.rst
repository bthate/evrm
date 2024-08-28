.. _manual:

.. raw:: html

    <br><br>

.. title:: Manual


**NAME**

    **EVRM** - 69389/12 `! <source.html>`_


**SYNOPSIS**

    ::

        evrm  <cmd> [key=val] [key==val]
        evrmc [-i] [-v]
        evrmd 


**DESCRIPTION**

    In 2012 heb ik het Europeese Hof voor de Rechten van de Mens aangeschreven om een klacht tegen Nederland in te dienen. De klacht betrof het afwezig zijn van verpleging in het nieuwe ambulante behandeltijdperk van de GGZ. Uitspraak is niet-ontvankelijk.


**INSTALL**

    ::

        $ pipx install evrm
        $ pipx ensurepath

        <new terminal>

        $ evrm srv > genocide.service
        # mv *.service /etc/systemd/system/
        # systemctl enable evrm --now

        joins #evrm on localhost


**USAGE**

    without any argument the bot does nothing

    ::

        $ evrm
        $

    see list of commands

    ::

        $ evrm cmd
        cmd,req,skl,srv


    start a console

    ::

        $ evrmc
        >

    start daemon

    ::

        $ evrmd
        $ 


    show request to the prosecutor

    ::

        $ evrm req
        Information and Evidence Unit
        Office of the Prosecutor
        Post Office Box 19519
        2500 CM The Hague
        The Netherlands


**CONFIGURATION**

    irc

    ::

        $ evrm cfg server=<server>
        $ evrmcfg channel=<channel>
        $ evrmcfg nick=<nick>

    sasl

    ::

        $ evrm pwd <nsvnick> <nspass>
        $ evrm cfg password=<frompwd>

    rss

    ::

        $ evrm rss <url>
        $ evrm dpl <url> <item1,item2>
        $ evrm rem <url>
        $ evrm nme <url> <name>


**COMMANDS**

    ::

        cfg - irc configuration
        cmd - commands
        mre - displays cached output
        pwd - sasl nickserv name/pass
        req - reconsider


**SOURCE**


    source is :ref:`here <source>`


**FILES**

    ::

        ~/.evrm 
        ~/.local/bin/evrm
        ~/.local/bin/evrmc
        ~/.local/bin/evrmd
        ~/.local/pipx/venvs/evrm/*


**AUTHOR**

    Bart Thate <bthate@dds.nl>


**COPYRIGHT**

    ``EVRM`` is Public Domain.
