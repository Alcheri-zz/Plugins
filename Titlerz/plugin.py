###
# Copyright (c) 2016, Barry Suridge
# All rights reserved.
#
###

import supybot.conf as conf
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.ircmsgs as ircmsgs
import supybot.callbacks as callbacks
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Titlerz')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x
# My plugins
try:
    # For Python 3.0 and later
    from urllib.request import urlopen
    from urllib.parse import urlparse
except ImportError:
    # Fall back to Python 2
    from urlparse import urlparse
    from urllib2 import urlopen
# Python library for pulling data out of HTML and XML files
from bs4 import BeautifulSoup
# A simple URL shortening Python Lib.
from pyshorteners import Shortener
# For error routines
import requests

class Titlerz(callbacks.Plugin):
    """Titlerz plugin."""

    def __init__(self, irc):
        self.__parent = super(Titlerz, self)
        self.__parent.__init__(irc)
        self.encoding = 'utf8'  # irc output.
        self.bitlylogin = self.registryValue('bitlyLogin')
        self.bitlyapikey = self.registryValue('bitlyApiKey')
        self.bitlytoken = self.registryValue('bitlyToken')

        # URL pyshorteners libraries.
        self.shortener = Shortener('Tinyurl')

        """
        List of domains of known URL shortening services.
        """
        self.services = [
            "adf.ly",
            "bit.do",
            "bit.ly",
            "bitly.com",
            "budurl.com",
            "cli.gs",
            "fa.by",
            "goo.gl",
            "is.gd",
            "j.mp",
            "lurl.no",
            "lnkd.in",
            "moourl.com",
            "ow.ly",
            "smallr.com",
            "snipr.com",
            "snipurl.com",
            "snurl.com",
            "su.pr",
            "t.co",
            "tiny.cc",
            "tr.im",
            "tinyurl.com"]

    def die(self):
        self.__parent.die()

    ##############
    # FORMATTING #
    ##############

    def _red(self, string):
        """Returns a red string."""
        return ircutils.mircColor(string, 'red')

    def _yellow(self, string):
        """Returns a yellow string."""
        return ircutils.mircColor(string, 'yellow')

    def _green(self, string):
        """Returns a green string."""
        return ircutils.mircColor(string, 'green')

    def _blue(self, string):
        """Returns a blue string."""
        return ircutils.mircColor(string, 'blue')

    def _bold(self, string):
        """Returns a non-bold string."""
        return ircutils.bold(string)

    def _nobold(self, string):
        """Returns a bold string."""
        return ircutils.stripBold(string)

    def _ul(self, string):
        """Returns an underline string."""
        return ircutils.underline(string)

    def _bu(self, string):
        """Returns a bold/underline string."""
        return ircutils.bold(ircutils.underline(string))

    ###############
    #  UTILITIES  #
    ###############

    def _cleantitle(self, msg):
        import re
        """Clean up the title of a URL."""

        cleaned = msg.translate(dict.fromkeys(range(32))).strip()
        return re.sub(r'\s+', ' ', cleaned)
    
    def _cleandesc(self, desc):
        """Tidies up description string."""

        desc = desc.replace('\n', '').replace('\r', '')
        return desc

    def _longurl(self, url):
        """Expand short URLs."""
        # URL shortening service.
        return self.shortener.expand(url)

    def _shorturl(self, url):
        """Shrink long URLs."""
        # URL shortening service.
        return self.shortener.short(url)
    
    def _getdesc(self):
        """Get webpage description - case-insensitive."""
        global desc, soup
        des = ''
        # Get webpage description
        des = soup.find('meta', attrs={'name': lambda x: x and x.lower()=='description'})
        if des and des.get('content'):
            desc = self._cleandesc(des['content'].strip())
        else:
            self.log.info("_getdesc: Not returning with content.")

    def _gettitle(self):
        """Get webpage title."""
        global title, soup
        try:
            title = self._cleantitle(soup.title.string) # Get webpage title
        except Exception as e:
            irc.reply(self._bold(self._red("ERROR: ")) + "{0}".format(e.reason), prefixNick=False)
            self.log.error("ERROR: {0}".format(e.reason))
            
    def doPrivmsg(self, irc, msg):
        """Monitor channel for URLs"""
        channel = msg.args[0]

        global title, desc, soup

        longurl = ''
        shorturl = ''
        text = ''
        title = ''
        desc = ''
        soup = ''

        # don't react to non-ACTION based messages.
        if ircmsgs.isCtcp(msg) and not ircmsgs.isAction(msg):
            return
        if irc.isChannel(channel):     # must be in channel.
            if ircmsgs.isAction(msg):  # if in action, remove.
                text = ircmsgs.unAction(msg)
            else:
                text = msg.args[1]

        for url in utils.web.urlRe.findall(text):
            try:
                if urlparse(url).hostname in self.services:
                    longurl = self._longurl(url)
                else:
                    shorturl = self._shorturl(url).replace('http://', '')
                soup = BeautifulSoup(urlopen(url).read(), 'lxml')  # Open the given URL
                self._gettitle()                                   # Get webpage title
                self._getdesc()                                    # Get webpage description
                if title:
                    s = self._bold(self._green("TITLE: ")) + title
                    irc.reply(s + " [{0}]".format(shorturl) if shorturl else s, prefixNick=False)  # prints: Title of webpage
                if desc:
                    irc.reply(self._bold(self._green("DESC : ")) + desc, prefixNick=False)         # prints: Webpage description
            except Exception as e:
                irc.reply(self._bold(self._red("ERROR: ")) + "{0}".format(e.reason), prefixNick=False)
                self.log.error("ERROR: {0}".format(e.reason))

    def url(self, irc, msg, args, url):
        """<url>

        Public test function for Titlez.
        Ex: http://www.google.com
        """
        global title, desc, soup

        channel = msg.args[0]
        user = msg.nick

        # self.log.info("Titlez: Trying to open: {0}".format(url))

        try:
            if urlparse(url).hostname in self.services:
                longurl = self._longurl(url)
                irc.reply(self._bold("URL  ") + ": {0}".format(longurl))
            else:
                shorturl = self._shorturl(url)
                irc.reply(self._bold("URL  ") + ": {0}".format(shorturl))
            soup = BeautifulSoup(urlopen(url).read(), 'lxml')  # Open the given URL
            self._gettitle()                                   # Get webpage title
            self._getdesc()                                    # Get webpage description
            if title:
                irc.reply(self._bold("TITLE: ") + title)       # prints: Title of webpage
            if desc:
                irc.reply(self._bold("DESC : ") + desc)
        except Exception as e:
            irc.reply(self._bold(self._red("ERROR: ")) + "{0}".format(e.reason), prefixNick=False)
            self.log.error("ERROR: {0}".format(e.reason))

    url = wrap(url, [('text')])

Class = Titlerz

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
