#!/usr/bin/env python
# coding: utf-8

###
# Copyright (c) 2016, Barry Suridge
# All rights reserved.
#
###

# Backward compatibility with Python 2 
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

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
# This module provides utilities for common tasks involving the with statement.
from contextlib import closing
# Regular expression operators
import re
# Plugin error traceback
import sys, traceback
# For Python 3.0 and later
from urllib.request import urlopen
from urllib.parse import urlparse, urlencode
# Python library for pulling data out of HTML and XML files
from bs4 import BeautifulSoup
from urllib.request import build_opener, Request

class Titlerz(callbacks.Plugin):
    """Titlerz plugin."""

    def __init__(self, irc):
        self.__parent = super(Titlerz, self)
        self.__parent.__init__(irc)
        self.encoding = 'utf8'  # irc output.

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
        """Clean up the title of a URL."""

        cleaned = msg.translate(dict.fromkeys(range(32))).strip()
        return re.sub(r'\s+', ' ', cleaned)
    
    def _cleandesc(self, desc):
        """Tidies up description string."""

        desc = desc.replace('\n', '').replace('\r', '')
        return desc
    
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

    # Create TinyURL link.
    def _make_tiny(self, url):
	    request_url = ('http://tinyurl.com/api-create.php?' + 
	        urlencode({'url':url}))
	    with closing(urlopen(request_url)) as response:
	        return response.read().decode('utf-8')
    
    # Open the webpage and parse
    def _getsoup(self, url):
       """Get web page."""
       opener = build_opener()
       opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux x86_64; rv:28.0) Gecko/20100101 Firefox/28.0')]
       req = Request(url)
       # Set language for page
       req.add_header('Accept-Language', 'en')
       response = opener.open(req)
       page = response.read()
       # Close open file
       response.close()
       soup = BeautifulSoup(page, 'lxml')
       return soup

    def doPrivmsg(self, irc, msg):
        """Monitor channel for URLs"""
        channel = msg.args[0]

        global desc, soup

        shorturl = ''
        text     = ''
        title    = ''
        desc     = ''
        soup     = ''
        t        = ''

        # first, check if we should be 'disabled' in this channel.
        # config channel #channel plugins.titlerz.enable True or False (or On or Off)
        if not self.registryValue('enable', channel):
            return
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
                if urlparse(url).hostname not in self.services:
                    shorturl = self._make_tiny(url).replace('http://', '')
                # Open the given URL and parse the HTML
                soup = self._getsoup(url)
                title = self._cleantitle(soup.title.string)  # Cleanup webpage title
                t = self._bold(self._blue("TITLE: ")) + title
                irc.reply(t + " [{0}]".format(shorturl) if shorturl else t, prefixNick=False)  # prints: Title of webpage
                # Get webpage description
                self._getdesc()
                if desc:
                    irc.reply(self._bold(self._blue("DESC : ")) + desc, prefixNick=False) # prints: Webpage description (if any)
            except (AttributeError, TypeError):
                self.log.error("Not found: " + url)
            except Exception as e:
                irc.reply(self._bold(self._red("ERROR: ")) + "{0}".format(e), prefixNick=False)
                # Non-fatal error traceback information
                self.log.info(traceback.format_exc())
                # or
                # self.log.info(sys.exc_info()[0])

    def url(self, irc, msg, args, url):
        """<url>

        Public test function for Titlez.
        Ex: url http://www.google.com
        """
        global desc, soup

        shorturl = ''
        desc     = ''
        title    = ''
        t        = ''

        # self.log.info("Titlez: Trying to open: {0}".format(url))

        if irc.network == "ChatLounge":
            irc.reply(irc.network)
        try:
            if urlparse(url).hostname not in self.services:
                shorturl = self._make_tiny(url).replace('http://', '')
            # Open the given URL and parse the HTML
            soup = self._getsoup(url)
            title = self._cleantitle(soup.title.string)  # Cleanup webpage title
            t = self._bold("TITLE: ") + title
            irc.reply(t + " [{0}]".format(shorturl) if shorturl else t) # prints: Title of webpage
            # Get webpage description
            self._getdesc()
            if desc:
                irc.reply(self._bold("DESC : ") + desc) # prints: Webpage description (if any)
        except (AttributeError, TypeError):
            self.log.error("Not found: " + url)
        except Exception as err:
            irc.reply(self._bold(self._red("ERROR: ")) + "{0}".format(err))
            self.log.error("ERROR: {0}".format(err))

    url = wrap(url, [('text')])

Class = Titlerz

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
