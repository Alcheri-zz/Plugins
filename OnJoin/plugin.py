###
# Copyright (c) 2016, Barry Suridge
# All rights reserved.
#
#
###

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
import random, os
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
        self.encoding = 'utf8'  # irc output.

    def die(self):
        self.__parent.die()

    def doJoin(self, irc, msg):
        channel = msg.args[0]
        # Check if we should be 'disabled' in this channel.
        # config channel #channel plugins.onjoin.enable True or False (or On or Off)
        if ircutils.isChannel(channel) and self.registryValue('enable', channel):
            try:
                p = os.path.expanduser('~')
                fp = p + '/runbot/plugins/OnJoin/quotes.txt'
                line_num = 0
                selected_line = ''
                with open(fp) as f:
                    while 1:
                        line = f.readline()
                        if not line: break
                        line_num += 1
                        if random.uniform(0, line_num) < 1:
                            selected_line = line
                # It's the bot.
                if ircutils.strEqual(irc.nick, msg.nick) is False:
                    irc.reply(color.bold(selected_line.strip()) , notice=True, private=True, to=msg.nick)
                else:
                    return None
            except Exception as err:
                irc.error("{0}".format(err))
        else:
            return None

Class = OnJoin


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
