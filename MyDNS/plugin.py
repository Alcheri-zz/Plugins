###
# Copyright (c) 2016 - 2021, Barry Suridge
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

import json    # JavaScript Object Notation
import socket  # Low-level networking interface
# For Python 3.3 and later
from urllib.parse import urlparse
from urllib.request import urlopen
from urllib.error import URLError
import ipaddress

from supybot.commands import *
import supybot.ircutils as utils
import supybot.callbacks as callbacks

    ###############
    #  FUNCTIONS  #
    ###############

special_chars = (
    '-',
    '[',
    ']',
    '\\',
    '`',
    '^',
    '{',
    '}',
    '_')

def is_nick(nick):
    """ Checks to see if a nickname `nick` is valid.
    According to :rfc:`2812 #section-2.3.1`, section 2.3.1, a nickname must start
    with either a letter or one of the allowed special characters, and after
    that it may consist of any combination of letters, numbers, or allowed
    special characters.
    """
    if not nick[0].isalpha() and nick[0] not in special_chars:
        return False
    for char in nick[1:]:
        if not char.isalnum() and char not in special_chars:
            return False
    return True

def is_ip(s):
    """Returns whether or not a given string is an IP address.
    """
    try:
        ipaddress.ip_address(s)
        # print(f'{ip} is a correct IP{ip.version} address.')
        return True
    except ValueError:
        # print(f'address/netmask is invalid: {s}')
        return False

def teal(string):
    """Return a teal coloured string."""
    return utils.bold(utils.mircColor(string, 'teal'))

class MyDNS(callbacks.Plugin):
    """An alternative to Supybot's DNS function.
    """

    def __init__(self, irc):
        super().__init__(irc)

    threaded = True

    ##############
    #    MAIN    #
    ##############

    @wrap(['text'])
    def dns(self, irc, msg, args, address):
        """<hostname | Nick | URL | IPv4 or IPv6>
        An alternative to Supybot's DNS function.
        Returns the ip of <hostname | Nick | URL | ip or IPv6> or the reverse
        DNS hostname of <ip> using Python's socket library
        """
        channel = msg.args[0]

        # Check if we should be 'disabled' in a channel.
        # config channel #channel plugins.mydns.enable True or False (or On or Off)
        if self.registryValue('enable', channel):
            if is_ip(address):
                irc.reply(self.gethostbyaddr(address), prefixNick=False)
            elif is_nick(address):  # Valid nick?
                nick = address
                try:
                    userHostmask = irc.state.nickToHostmask(nick)
                    (nick, _, host) = utils.splitHostmask(userHostmask)  # Returns the nick and host of a user hostmask.
                    irc.reply(self.gethostbyaddr(host), prefixNick=False)
                except KeyError:
                    irc.reply(f"[{nick}] is unknown.", prefixNick=False)
            else:  # Neither IP or IRC user nick.
                irc.reply(self.getaddrinfo(address), prefixNick=False)
        else:
            return

    def getaddrinfo(self, host):
        """Get host information. Use returned IP address
        to find the (approximate) geolocation of the host.
        """
        host = host.lower()
        d = urlparse(host)

        if d.scheme:
            host = d.netloc

        try:
            result = socket.getaddrinfo(host, None)
        except OSError as err:  # Catch failed address lookup.
            return (f'OS error: {err}')
        except IOError as err:
            return '%r There was an error.' % err

        ipaddress = result[0][4][0]
        geoip = self.geoip(ipaddress)

        dns = teal('DNS: ')
        loc = teal('LOC: ')

        return (f'{dns}{host} resolves to [{ipaddress}] {loc}{geoip}')

    def gethostbyaddr(self, ip):
        """Do a reverse lookup for ip.
        """
        try:
            (hostname, _, address) = socket.gethostbyaddr(ip)
            hostname = hostname + ' <> ' + address[0]
            geoip = self.geoip(address[0])
            shortname = hostname.split('.')[0]
            dns = teal('DNS:')
            loc = teal('LOC:')
            return (f'{dns} <{shortname}> [{hostname}] {loc} {geoip}')
        except OSError as err:  # Catch address-related errors.
            return (f'OS error: {err}')
        except IOError as err:
            return '%r There was an error.' % err

    def geoip(self, address):
        """Search for the geolocation of IP addresses.
        Accuracy not guaranteed.
        """
        apikey = self.registryValue('ipstackAPI')

        if not apikey:
            raise callbacks.Error(_( \
                'Please configure the ipstack API key in config plugins.MyDNS.ipstackAPI'))

        try:
            url = 'http://api.ipstack.com/' + address + '?access_key=' + apikey
            response = urlopen(url, timeout=1).read().decode('utf8')
        except URLError as err:
            if hasattr(err, 'reason'):
                return (f'We failed to reach a server. Reason: {err.reason}')
            else:
                return (f'The server couldn\'t fulfill the request: {err}')
        except socket.timeout:
            return (f'Socket timed out - URL {url}')
        else:
            data = json.loads(response)

        _city    = 'City:%s ' % data['city'] if data['city'] else ''
        _state   = 'State:%s ' % data['region_name'] if data['region_name'] else ''
        #_tmz     = 'TMZ:%s ' % data['time_zone'] if data['time_zone'] else ''
        _long    = 'Long:%s ' % data['longitude'] if data['longitude'] else ''
        _lat     = 'Lat:%s ' % data['latitude'] if data['latitude'] else ''
        _code    = 'Country Code:%s ' % data['country_code'] if data['country_code'] else ''
        _country = 'Country:%s ' % data['country_name'] if data['country_name'] else ''
        _zip     = 'Post/Zip Code:%s' % data['zip'] if data['zip'] else ''

        s = ''
        seq = [_city, _state, _long, _lat, _code, _country, _zip]

        return (s.join( seq ))

Class = MyDNS

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
