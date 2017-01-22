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
        # It's us.
        if ircutils.strEqual(irc.nick, msg.nick):
            return None
        # check if 'disabled' in this channel.
        if ircutils.isChannel(channel):
            if self.registryValue('enabled', msg.args[0]) and \
                len(msg.args) > 1:
                m = 'We are the Borg. Resistance is futile.'
                irc.reply(m, notice=True, private=True, to=msg.nick)
            else:
                return None

    def enable(self, irc, msg, args, channel):
        """
        [<channel>]
        Enables this plugin in <channel> messages the bot sees.
        <channel> is only necessary if the message
        isn't sent in the channel itself.
        """
        self.setRegistryValue('enabled', True, channel)
        irc.replySuccess()
    enable = wrap(enable, ['channel'])

    def disable(self, irc, msg, args, channel):
        """
        [<channel>]
        Disables this plugin in <channel>.  <channel> is only necessary if the
        message isn't sent in the channel itself.
        """
        self.setRegistryValue('enabled', False, channel)
        irc.replySuccess()
    disable = wrap(disable, ['channel'])

Class = OnJoin


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
