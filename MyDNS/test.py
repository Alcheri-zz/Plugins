###
# Copyright (c) 2016, Barry Suridge
# All rights reserved.
#
#
###

from supybot.test import *
import supybot.conf as conf


class MyDNSTestCase(PluginTestCase):
    plugins = ('MyDNS',)

    def testSimple(self):
        self.assertNotError('mydns dns google.com')
        self.assertNotError('mydns dns 2a03:2880:f119:8083:face:b00c:0:25de')
        
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
