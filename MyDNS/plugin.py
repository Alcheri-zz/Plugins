##
# Copyright (c) 2016 - 2020, Barry Suridge
# All rights reserved.
#
#
###

# My plugins
import json    # JavaScript Object Notation
import socket  # Low-level networking interface
import validators # Python Data Validation for Humans
# For Python 3.0 and later
from urllib.parse import urlparse
from urllib.request import urlopen
from urllib.error import URLError

from supybot.commands import *
import supybot.ircutils as utils
import supybot.callbacks as callbacks

try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('MyDNS')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x

    ###############
    #  FUNCTIONS  #
    ###############
def is_valid_ip(ipaddress):
    """Validates IP addresses.
    """
    ip = validators.ip_address.ipv4(ipaddress) or validators.ip_address.ipv6(ipaddress)
    return ip

class MyDNS(callbacks.Plugin):  # pylint: disable=too-many-ancestors
    """An alternative to Supybot's DNS function.
    """

    def __init__(self, irc):
        super().__init__(irc)

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

    ##############
    #    MAIN    #
    ##############

    def dns(self, irc, msg, args, address):
        """<hostname | Nick | URL | IPv4 or IPv6>
        An alternative to Supybot's DNS function.
        Returns the ip of <hostname | Nick | URL | ip or IPv6> or the reverse
        DNS hostname of <ip> using Python's socket library
        """
        if is_valid_ip(address):
            irc.reply(self._gethostbyaddr(address), prefixNick=False)
        elif self._isnick(address):  # Valid nick?
            nick = address
            try:
                userHostmask = irc.state.nickToHostmask(nick)
                (nick, _, host) = utils.splitHostmask(userHostmask)  # Returns the nick and host of a user hostmask.
                irc.reply(self._gethostbyaddr(host), prefixNick=False)
            except KeyError:
                irc.error('No such nick.', Raise=True)
        else:  # Neither IP or IRC user nick.
            irc.reply(self._getaddrinfo(address), prefixNick=False)	    

    dns = wrap(dns, ['something'])

    def _getaddrinfo(self, host):
        """Get host information. Use returned IP address
        to find the (approximate) geolocation of the host.
        """
        d = urlparse(host)

        if d.scheme:
            host = d.netloc

        try:
            result = socket.getaddrinfo(host, None)
        except socket.gaierror as msg:  # Catch failed address lookup.
            return Exception(msg)
            
        ipaddress = result[0][4][0]
        geoip = self._geoip(ipaddress)

        dns = self._teal('DNS: ')
        loc = self._teal('LOC: ')

        return '%s%s resolves to [%s] %s%s' % (dns, host, ipaddress, loc, geoip)

    def _gethostbyaddr(self, ip):
        """Do a reverse lookup for ip.
        """
        try:
            (hostname, _, addresses) = socket.gethostbyaddr(ip)
        except socket.herror as msg:  # Catch failed ip address lookup.
            return Exception(msg)

        address = addresses[0]
        geoip = self._geoip(address)
        vip = is_valid_ip(ip)

        dns = self._teal('DNS: ')
        loc = self._teal('LOC: ')

        # Check whether 'ip' consists of alphabetic characters - VHost. Print output accordingly.
        if not vip:
            return '%s%s resolves to [%s] %s%s' % (dns, hostname, address, loc, geoip)

        return '%s%s resolves to [%s] %s%s' % (dns, address, hostname, loc, geoip)

    def _geoip(self, address):
        """Search for the geolocation of IP addresses.
        Accuracy not guaranteed.
        """
        apikey = self.registryValue('apikeys.ipstack')
		
        if not apikey:
            raise Exception('No API key defined')

        url = 'http://api.ipstack.com/' + address + '?access_key=' + apikey

        try:
            response = urlopen(url, timeout=1).read().decode('utf8')
        except OSError as err:
            if hasattr(err, 'reason'):
                return 'We failed to reach a server. Reason: %s' % err.reason
            elif hasattr(err, 'code'):
                return 'The server couldn\'t fulfill the request: %s' % err.code
        data = json.loads(response)

        _city    = 'City:%s ' % data['city'] if data['city'] else ''
        _state   = 'State:%s ' % data['region_name'] if data['region_name'] else ''
        #_tmz     = 'TMZ:%s ' % data['time_zone'] if data['time_zone'] else ''
        _long    = 'Long:%s ' % data['longitude'] if data['longitude'] else ''
        _lat     = 'Lat:%s ' % data['latitude'] if data['latitude'] else ''
        _code    = 'Country Code:%s ' % data['country_code'] if data['country_code'] else ''
        _country = 'Country:%s ' % data['country_name'] if data['country_name'] else ''
        _zip     = 'Post/Zip Code:%s' % data['zip'] if data['zip'] else ''

        return ''.join([_city, _state, _long, _lat, _code, _country, _zip])

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

    def _teal(self, string):
        """Return a teal coloured string."""
        return utils.bold(utils.mircColor(string, 'teal'))

Class = MyDNS

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
