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
import validators as valid
from urllib.parse import urlparse
import re, requests, socket
import sys, traceback # Error traceback
import errno # Standard errno system symbols

try:
    from supybot.i18n import PluginInternationalization, internationalizeDocstring
    _ = PluginInternationalization('MyDNS')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x
# Text formatting library
try:
    from .local import color
except ImportError:
    from color import *

class MyDNS(callbacks.Plugin):
    """An alternative to Supybot's DNS function."""

    def __init__(self, irc):
        self.__parent = super(MyDNS, self)
        self.__parent.__init__(irc)
        self.encoding = 'utf8'  # irc output.

        self._special_chars = (
            '-',
            '[',
            ']',
            '\\',
            '`',
            '^',
            '{',
            '}',
            '_')

    def die(self):
        self.__parent.die()

    def dns(self, irc, msg, args, i):
        """<hostname | Nick | URL | ip or IPv6>
        An alternative to Supybot's DNS function.
        Returns the ip of <hostname | Nick | URL | ip or IPv6> or the reverse DNS hostname of <ip> using Python's socket library.
        """

        channel = msg.args[0]

        if not irc.isChannel(channel):
            return

        name =''
        ip_address_list = ''
        userHostmask = ''
        dns = color.bold(color.teal('DNS: '))
        geoip = color.bold(color.teal('LOC: '))

        if self._isnick(i):  # Valid bnick?
            nick = i
            if not nick.lower() in irc.state.channels[channel].users:
                irc.error('No such nick.', prefixNick=False)
                return
            try:
                userHostmask = irc.state.nickToHostmask(nick)
            except KeyError:
                irc.error('Invalid nick or hostmask', prefixNick=False)
                return

            (nick, user, host) = ircutils.splitHostmask(userHostmask)
            try:
                (name, _, ip_address_list) = socket.gethostbyaddr(host)
                if (valid.ip_address.ipv4(host) or valid.ip_address.ipv6(host)): # Check if input is a valid IPv4 or IPv6 address.
                   irc.reply(dns + ip_address_list[0] + ' resolves to ' + name, prefixNick=False)
                else:
                    irc.reply(dns + name + ' resolves to ' + ip_address_list[0], prefixNick=False)
                irc.reply(geoip + self._geoip(ip_address_list[0]), prefixNick=False)
            except socket.gaierror as err:
                irc.error("{0}".format(err), prefixNick=False)
            except:
                pass

        if valid.domain(i): # Check if input is a domain.
            try:
                (name, _, ip_address_list) = socket.gethostbyname_ex(i)
                irc.reply(dns + name + ' resolves to {0}'.format(ip_address_list[0]), prefixNick=False)
                irc.reply(geoip + self._geoip(ip_address_list[0]), prefixNick=False)
            except socket.gaierror as err:
                try:
                    (name, _, ip_address_list) = socket.gethostbyaddr(i)
                except:
                    irc.reply('Dns unable to resolve address ' + i, prefixNick=False)
                    return
                irc.reply(dns + name + ' resolves to ' + ip_address_list[0], prefixNick=False)
                irc.reply(geoip + self._geoip(ip_address_list[0]), prefixNick=False)                   
        elif valid.url(i): # Check if input is a valid URL.
            o = urlparse(i)
            s = i.replace(o.scheme + "://", "")
            try:
                (name, _, ip_address_list) = socket.gethostbyname_ex(s)
                irc.reply(dns + s + ' resolves to {0}'.format(ip_address_list[0]), prefixNick=False)
                irc.reply(geoip + self._geoip(ip_address_list[0]), prefixNick=False)
            except socket.gaierror as err:
                irc.error("{0}".format(err), prefixNick=False)
        elif (valid.ip_address.ipv4(i) or valid.ip_address.ipv6(i)): # Check if input is a valid IPv4 or IPv6 address.
            try:                
                (name, _, ip_address_list) = socket.gethostbyaddr(i)
                irc.reply(dns + ip_address_list[0] + ' resolves to ' + name, prefixNick=False)
                irc.reply(geoip + self._geoip(ip_address_list[0]), prefixNick=False)
            except Exception as err:
                if err.errno == 2:
                    irc.reply('Dns Host name lookup failure ' + i, prefixNick=False)
                else:
                    irc.reply('An error has occurred and has been logged. Please contact this bot\'s administrator for more information.')
                    # Non-fatal error traceback information
                    self.log.info(traceback.format_exc())
        else:
            return

    dns = wrap(dns, ['something'])

    def _isnick(self, nick):
        """ Checks to see if a nickname `nick` is valid.
        According to :rfc:`2812 #section-2.3.1`, section 2.3.1, a nickname must start
        with either a letter or one of the allowed special characters, and after
        that it may consist of any combination of letters, numbers, or allowed 
        special characters.
        """

        if not nick[0].isalpha() and nick[0] not in self._special_chars:
            return False
        for char in nick[1:]:
            if not char.isalnum() and char not in self._special_chars:
                return False
        return True

    def _geoip(self, ip):
        """Search the geolocation of IP addresses."""
        from urllib.request import urlopen
        import json

        url = 'http://freegeoip.net/json/' + ip
        try:
            response = urlopen(url, timeout = 1).read().decode('utf8')
        except URLError as err:
            # Non-fatal error traceback information
            self.log.info(traceback.format_exc())
        except socket.timeout as err:
            raise MyException('There was an error: %r' % err)
        data = json.loads(response)

        location_city = data['city']
        location_state = data['region_name']
        location_tmz = data['time_zone']
        location_long = data['longitude']
        location_lat = data['latitude']
        location_code = data['country_code']
        location_country = data['country_name']
        location_zip = data['zip_code']

        return "City:{0}".format(location_city) + " State:{0}".format(location_state) + " TMZ:{0}".format(location_tmz) + " Long:{0}".format(location_long) +\
            " Lat:{0}".format(location_lat) + " Country Code:{0}".format(location_code) +" Country:{0}".format(location_country) + " Post/Zip Code:{0}".format(location_zip)

class MyException(Exception):
    pass

MyDNS = internationalizeDocstring(MyDNS)

Class = MyDNS


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
