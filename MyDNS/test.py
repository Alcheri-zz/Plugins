###
# Copyright (c) 2020, Barry Suridge
# All rights reserved.
#
#
###
import socket

from supybot.test import *
import supybot.conf as conf

class MyPluginTestCase(PluginTestCase):
    def testThisThing(self):
        with conf.supybot.commands.nested.context(False):
            self.assertNotError(socket.gethostbyaddr('203.208.60.1'))
            self.assertRegexp(socket.gethostbyaddr('localhost', '127\.0\.0\.1'))

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
