###
# Copyright (c) 2020, Barry Suridge
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###
import sys
import shlex
import subprocess
import re
import validators

###
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('MyPing')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x:x

    ###############
    #  FUNCTIONS  #
    ###############
# Text colour formatting library
from .local import color

def _Validate (host):
    if not validators.domain(host):
        if validators.ip_address.ipv4(host) or validators.ip_address.ipv6(host):
	        return True
        else:
            return False
    else:
        return True

def _GetMatch (output):
    match = re.search('([\d]*\.[\d]*)/([\d]*\.[\d]*)/([\d]*\.[\d]*)/([\d]*\.[\d]*)', str(output))
	
    ping_min = match.group(1)
    ping_avg = match.group(2)
    ping_max = match.group(3)

    match = re.search('(\d*)% packet loss', str(output))
    pkt_loss = match.group(1)
	
    return str(pkt_loss)

class MyPing(callbacks.Plugin):

    def __init__(self, irc):
		
        self.__parent = super(MyPing, self)
        self.__parent.__init__(irc)

    threaded = True

    def pingz(self, irc, msg, args, address):
        """An alternative to Supybot's PING function."""

        txt = color.bold(color.teal(' Is invalid!'))

        if _Validate (address):    
            cmd = shlex.split("ping -c1 " + str(address))       
            try:
                output = subprocess.check_output(cmd)
                pkt_loss = _GetMatch (output)
            except subprocess.CalledProcessError as err:
            #Will print the command failed
                irc.reply("{0} is Not Reachable".format(cmd[-1]))
            else:
                irc.reply("{0} is Reachable ~".format(cmd[-1]) + " Packet Loss: " + pkt_loss+"%")
        else:
            irc.reply(address + txt)

    pingz = wrap(pingz, ['something'])
    
Class = MyPing

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
