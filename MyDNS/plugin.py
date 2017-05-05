###
# coding: utf-8
##
# Copyright (c) 2016, Barry Suridge
# All rights reserved.
#
#
###
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

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

try:
    from supybot.i18n import PluginInternationalization, internationalizeDocstring
    _ = PluginInternationalization('MyDNS')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x
# Text colour formatting library
from .local import color

class MyDNS(callbacks.Plugin):
    """An alternative to Supybot's DNS function.
    """

    def __init__(self, irc):
        self.__parent = super().__init__(irc)
               
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
        Returns the ip of <hostname | Nick | URL | ip or IPv6> or the reverse
        DNS hostname of <ip> using Python's socket library.
        """
        channel = msg.args[0]
        
        if self.is_valid_ip(address):
                irc.reply(self._gethostbyaddr(address), prefixNick=False) # Reverse lookup.
        elif self._isnick(address):  # Valid nick?
            nick = address
            #if not nick.lower() in irc.state.channels[channel].users: # Not in channel.
            #    irc.error('No such nick.', Raise=True)
            try:
                userHostmask = irc.state.nickToHostmask(nick)
                (nick, user, host) = ircutils.splitHostmask(userHostmask) # Split the channel users hostmask.           
                irc.reply(self._gethostbyaddr(host), prefixNick=False) # Reverse lookup.
            except KeyError:
                irc.error('No such nick.', Raise=True)
        else:
            irc.reply(self._getaddrinfo(address), prefixNick=False)
            
    dns = wrap(dns, ['something'])
    
    def _getaddrinfo(self, host):
        """Resolve host and gather available IP addresses and use
        them to find the geolocation of the host.
        """

        d = urlparse(host)
        
        if d.scheme:
            host = d.netloc
        
        try:
            result = socket.getaddrinfo(host, None)
        except socket.timeout as err: # Timed out trying to connect.
            return '{}'.format(err)
        except socket.gaierror as err:
            return '{}'.format(err)

        ipaddress = result[0][4][0]        
        geoip = self._geoip(ipaddress)
        dns = color.bold(color.teal('DNS: '))
        loc = color.bold(color.teal('LOC: '))
        
        return '%s%s resolves to [%s] %s%s' % (dns, host, ipaddress, loc, geoip)               
    
    def _gethostbyaddr(self, ip):
        """Do a reverse lookup for ip.
        """  
        try:
            (hostname, _, addresses) = socket.gethostbyaddr(ip)
        except socket.timeout as err: # Name/service not known or failure in name resolution
            return '{}'.format(err)
        except socket.error as err: # Catch any errors.
            return '{}'.format(err)

        geoip = self._geoip(addresses[0])
 
        dns = color.bold(color.teal('DNS: '))
        loc = color.bold(color.teal('LOC: '))

        if not self.is_valid_ip(ip): # Check whether 'ip' consists of alphabetic characters only. Print output accordingly.
            return '%s%s resolves to [%s] %s%s' % (dns, hostname, addresses[0], loc, geoip)
        else:
            return '%s%s resolves to [%s] %s%s' % (dns, addresses[0], hostname, loc, geoip)
    
    def _getipv6(self, host, port=0):
        """Search only for the wanted IPv6 addresses.
        """
        try:
            result = socket.getaddrinfo(host, port, socket.AF_INET6)
        except Exception as err:
            return None
        # return result # or:
        return result[0][4][0] # Just returns the first answer and only the address.

    def is_valid_ip(self, ip):
        """Validates IP addresses.
        """
        return self.is_valid_ipv4(ip) or self.is_valid_ipv6(ip)
    
    def is_valid_ipv4(self, address):
        """Validates IPv4 addresses.
        """
        try:
            socket.inet_pton(socket.AF_INET, address)
        except AttributeError:  # No inet_pton here, sorry.
            try:
                socket.inet_aton(address)
            except socket.error:
                return False
            return address.count('.') == 3
        except socket.error:  # Not a valid address.
            return False
        return True
    
    def is_valid_ipv6(self, address):
        """Validates IPv6 addresses.
        """
        try:
            socket.inet_pton(socket.AF_INET6, address)
        except socket.error:  # Not a valid address.
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

    def _geoip(self, ip, response=None, data=None):
        """Search for the geolocation of IP addresses.
        Accuracy not guaranteed.
        """

        url = 'http://freegeoip.net/json/' + ip
        
        try:
            response = urlopen(url, timeout = 1).read().decode('utf8')
        except URLError as err:
            if hasattr(err, 'reason'):
                return 'We failed to reach a server. Reason: {}'.format(err.reason)
            elif hasattr(err, 'code'):
                return 'The server couldn\'t fulfill the request: {}'.format(err.code)
        data = json.loads(response)
       
        _city    = 'City:%s ' % data['city'] if data['city'] else ''
        _state   = 'State:%s ' % data['region_name'] if data['region_name'] else ''
        _tmz     = 'TMZ:%s ' % data['time_zone'] if data['time_zone'] else ''
        _long    = 'Long:%s ' % data['longitude'] if data['longitude'] else ''
        _lat     = 'Lat:%s ' % data['latitude'] if data['latitude'] else ''
        _code    = 'Country Code:%s ' % data['country_code'] if data['country_code'] else ''
        _country = 'Country:%s ' % data['country_name'] if data['country_name'] else ''
        _zip     = 'Post/Zip Code:%s' % data['zip_code'] if data['zip_code'] else ''

        return ''.join([_city, _state, _tmz, _long, _lat, _code, _country, _zip])

Class = MyDNS

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
