##
# Copyright (c) 2016, Barry Suridge
# All rights reserved.
#
#
###
from __future__ import print_function

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
# For Python 3.0 and later
from urllib.parse import urlparse
from urllib.request import urlopen
from urllib.error import URLError
# My plugins
import json   # JavaScript Object Notation
import socket # Low-level networking interface
import sys, traceback # Error traceback

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
    """An alternative to Supybot's DNS function.
    """

    def __init__(self, irc):
        self.__parent = super(MyDNS, self)
        self.__parent.__init__(irc)
        self.encoding = 'utf8'  # irc output.
        
        geoloc    = None
        hostname  = None
        addresses = None
        
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
        
    threaded = True
    
    def dns(self, irc, msg, args, address):
        """<hostname | Nick | URL | ip or IPv6>
        An alternative to Supybot's DNS function.
        Returns the ip of <hostname | Nick | URL | ip or IPv6> or the reverse DNS hostname of <ip> using Python's socket library.
        """
        channel = msg.args[0]
        
        if not irc.isChannel(channel):
            return

        dns = color.bold(color.teal('DNS: '))
        loc = color.bold(color.teal('LOC: '))

        if self._isnick(address):  # Valid nick?
            nick = address
            if not nick.lower() in irc.state.channels[channel].users:
                irc.error('No such nick.', prefixNick=False)
                return
            try:
                userHostmask = irc.state.nickToHostmask(nick)
            except KeyError:
                irc.error('Invalid nick or hostmask', prefixNick=False)
                return

            (nick, user, host) = ircutils.splitHostmask(userHostmask) # Split the channel users hostmask.
            
            self._gethostbyaddr(host) # Get the IPv4 or IPv6 address of the channel user.
            # Format the output.
            if (self.is_valid_ip(host)): # Check if host is a valid IPv4 or IPv6 address.
               irc.reply(dns + addresses[0] + ' resolves to [\'{}\']'.format(hostname), prefixNick=False)
            else:
                irc.reply(dns + hostname + ' resolves to [\'{}\']'.format(addresses[0]), prefixNick=False)
        else: # Is not a channel user nick.
            if self.is_valid_ip(address): # Check if input is a valid IPv4 or IPv6 address.
                ip = address
                irc.reply(dns + self._gethostbyaddr(ip), prefixNick=False)
            elif (address[:7] == 'http://' or "www." in address): # Check if input is valid.
                domain = address
                irc.reply(dns + self._gethostbyname(domain), prefixNick=False)
            else:
                irc.reply(dns + self._gethostbyaddr_(address), prefixNick=False)
        if geoloc: # Print the geolocation of the domain or IPv4 or IPv6 address.
            irc.reply(loc + geoloc, prefixNick=False)
            
        return

    dns = wrap(dns, ['something'])

    def _gethostbyname(self, domain):
        """Translate a host name to IPv4 or IPv6 address format.
        """
        global geoloc
        d = urlparse(domain)
        
        if d.scheme:
            domain = d.netloc

        try:
            (hostname, aliaslist, ipaddrlist) = socket.gethostbyname_ex(domain)
        except socket.error as err:
            geoloc = ''
            return "{}".format(err)
        
        geoloc = self._geoip(ipaddrlist[0])
        getfqdn = socket.getfqdn(domain)
        return domain + ' resolves to {} [\'{}\'] [\'{}\'] {}'.format(ipaddrlist, hostname, getfqdn, aliaslist if aliaslist else '')
    
    def _gethostbyaddr(self, ip):
        """Do a reverse lookup for ip.
        """
        global geoloc, hostname, addresses
        try:       
            (hostname, aliases, addresses) = socket.gethostbyaddr(ip)
        except socket.error as err:
            geoloc = ''
            return "{}".format(err)
        
        geoloc = self._geoip(addresses[0])

        return ip + ' resolves to [\'{}\'] {} {}'.format(hostname, aliases if aliases else '', addresses)
    
    def is_valid_ip(self, ip):
        """Validates IP addresses.
        """
        return self.is_valid_ipv4(ip) or self.is_valid_ipv6(ip)
    
    def is_valid_ipv4(self, address):
        """Validates IPv4 addresses.
        """
        try:
            socket.inet_pton(socket.AF_INET, address)
        except AttributeError:  # no inet_pton here, sorry
            try:
                socket.inet_aton(address)
            except socket.error:
                return False
            return address.count('.') == 3
        except socket.error:  # not a valid address
            return False
        return True
    
    def is_valid_ipv6(self, address):
        """Validates IPv6 addresses.
        """
        try:
            socket.inet_pton(socket.AF_INET6, address)
        except socket.error:  # not a valid address
            return False
        return True

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
        """Search for the geolocation of IP addresses.
        """

        url = 'http://freegeoip.net/json/' + ip
        response = ''
        try:
            response = urlopen(url, timeout = 1).read().decode('utf8')
        except URLError as err:
            if hasattr(err, 'reason'):
                return 'We failed to reach a server. Reason: {0}'.format(err.reason)
            elif hasattr(err, 'code'):
                return 'The server couldn\'t fulfill the request: {0}'.format(err.code)
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

Class = MyDNS

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
