# pylint: disable=missing-docstring
# pylint: disable=unused-argument
# pylint: disable=invalid-name

##
# Copyright (c) 2016 - 2020, Barry Suridge
# All rights reserved.
#
# Python 3 and above ONLY!
###

import random
import os.path

import supybot.ircutils as utils
import supybot.callbacks as callbacks
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('OnJoin')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x

class OnJoin(callbacks.Plugin):  # pylint: disable=too-many-ancestors
    """Send a notice to all users entering a channel."""

    public = False

    def __init__(self, irc):
        self.__parent = super().__init__(irc)

    def doJoin(self, irc, msg):
        """Send a random notice to a user
        when they enter the channel."""

        channel = msg.args[0]

        # Check if in a channel and see if we should be 'disabled' in it.
        # config channel #channel plugins.onjoin.enable True or False (or On or Off)
        if self.registryValue('enable', channel):
            p = os.path.abspath(os.path.dirname(__file__))
            p = p + '/quotes.txt'
            fp = str(p)
            line_num = 0
            selected_line = ''
            try:
                with open(fp) as f:
                    while 1:
                        line = f.readline()
                        if not line:
                            break
                        line_num += 1
                        if random.uniform(0, line_num) < 1:
                            selected_line = line
                # It's not the bot.
                if utils.strEqual(irc.nick, msg.nick) is False:
                    irc.reply(self._teal(selected_line.strip()), notice=True, private=True, to=msg.nick)
                else:
                    pass
            except IOError as err:
                # Non-fatal error traceback information
                raise (FileError('failed to open'), err)
        else:
            return

    def _teal(self, string):
        """Return a teal coloured string."""
        return utils.bold(utils.mircColor(string, 'teal'))

class FileError(Exception):
    """Non-fatal error traceback."""
    pass

Class = OnJoin


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
