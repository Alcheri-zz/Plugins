###
# Copyright (c) 2016, Barry Suridge
# All rights reserved.
#
# Python 3
###
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from future.utils import raise_from
from builtins import *

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('OnJoin')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x
import random
from pathlib import Path
# Text formatting library
try:
    from .local import color
except ImportError:
    from color import *

class OnJoin(callbacks.Plugin):
    """Send a notice to all users entering a channel."""

    public = False

    def __init__(self, irc):
        self.__parent = super(OnJoin, self)
        self.__parent.__init__(irc)

    def die(self):
        self.__parent.die()

    def doJoin(self, irc, msg):
        channel = msg.args[0]
        # Check if in a channel and see if we should be 'disabled' in it.
        # config channel #channel plugins.onjoin.enable True or False (or On or Off)
        if ircutils.isChannel(channel) and self.registryValue('enable', channel):
            p = Path('plugins/OnJoin/quotes.txt').resolve()
            fp = str(p)
            line_num = 0
            selected_line = ''
            try:
                with open(fp) as f:
                    while 1:
                        line = f.readline()
                        if not line: break
                        line_num += 1
                        if random.uniform(0, line_num) < 1:
                            selected_line = line
                # It's not the bot.
                if ircutils.strEqual(irc.nick, msg.nick) is False:
                    irc.reply(color.teal(selected_line.strip()) , notice=True, private=True, to=msg.nick)
                else:
                    return None
            except IOError as err:
                # Non-fatal error traceback information
                raise_from(DatabaseError('failed to open'), err)
        else:
            return None

class DatabaseError(Exception):
    pass

Class = OnJoin


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
