#!/usr/bin/env python3
# coding: utf-8

###
# Copyright (c) 2016, Barry Suridge
# All rights reserved.
#
###

# Backwards compatibility with Python 2 
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
from urllib.request import HTTPError, Request, urlopen
from urllib.parse import urlparse, urlencode
# Python library for pulling data out of HTML and XML files
from bs4 import BeautifulSoup
import requests

class Titlerz(callbacks.Plugin):
    """Titlerz plugin."""
    threaded = True
    noIgnore = False

    def __init__(self, irc):
        self.__parent = super(Titlerz, self)
        self.__parent.__init__(irc)
        self.encoding = 'utf8'  # irc output.

        """
        List of domains of known URL shortening services.
        """
        self.shortUrlServices = [
            'adf.ly',
            'bit.do',
            'bit.ly',
            'bitly.com',
            'budurl.com',
            'cli.gs',
            'fa.by',
            'goo.gl',
            'is.gd',
            'j.mp',
            'lurl.no',
            'lnkd.in',
            'moourl.com',
            'ow.ly',
            'smallr.com',
            'snipr.com',
            'snipurl.com',
            'snurl.com',
            'su.pr',
            't.co',
            'tiny.cc',
            'tr.im',
            'tinyurl.com']

        """
        List of domains to not allow displaying
        of web page descriptions.
        """
        self.baddomains = [
            'twitter.com',
            'panoramio.com',
            'kickass.to',
            'tinypic.com',
            'ebay.com',
            'imgur.com',
            'dropbox.com']

    def die(self):
        self.__parent.die()

    ##############
    # FORMATTING #
    ##############

    def _white(self, string):
        """Returns a white string."""
        return ircutils.mircColor(string, 'white')

    def _black(self, string):
        """Returns a black string."""
        return ircutils.mircColor(string, 'black')

    def _blue(self, string):
        """Returns a blue string."""
        return ircutils.mircColor(string, 'blue')

    def _green(self, string):
        """Returns a green string."""
        return ircutils.mircColor(string, 'green')
    
    def _red(self, string):
        """Returns a red string."""
        return ircutils.mircColor(string, 'red')

    def _brown(self, string):
        """Returns a brown string."""
        return ircutils.mircColor(string, 'brown')

    def _purple(self, string):
        """Returns a purple string."""
        return ircutils.mircColor(string, 'purple')

    def _orange(self, string):
        """Returns a orange string."""
        return ircutils.mircColor(string, 'orange')

    def _yellow(self, string):
        """Returns a yellow string."""
        return ircutils.mircColor(string, 'yellow')

    def _light_green(self, string):
        """Returns a light green string."""
        return ircutils.mircColor(string, 'light green')
    
    def _teal(self, string):
        """Returns a teal string."""
        return ircutils.mircColor(string, 'teal')

    def _light_blue(self, string):
        """Returns a light blue string."""
        return ircutils.mircColor(string, 'light blue')

    def _dark_blue(self, string):
        """Returns a dark blue string."""
        return ircutils.mircColor(string, 'dark blue')

    def _pink(self, string):
        """Returns a pink string."""
        return ircutils.mircColor(string, 'pink')

    def _dark_grey(self, string):
        """Returns a dark grey string."""
        return ircutils.mircColor(string, 'dark grey')

    def _light_grey(self, string):
        """Returns a light gray string."""
        return ircutils.mircColor(string, 'light gray')

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

    #########################
    # HTTP HELPER FUNCTIONS #
    #########################

    def open_url(self, url, gd=True):
        """Generic http fetcher we can use here.
           Links are handled here and passed on.
        """
        import os
        # big try except block and error handling for each.
        self.log.info("open_url: Trying to open: {0}".format(url))

        desc = None
        o    = None
        shorturl = None
        longurl  = None

        # Check for bad media extensions.
        if url.endswith(('.flv', '.m3u8')):
            path = urlparse(url).path
            ext = os.path.splitext(path)[1]
            return "open_url: ERROR. Bad extention " + ext
        # Requests: HTTP for Humans
        req = Request(url)
        try:
            res = urlopen(req, timeout=4)
        except HTTPError as err:
            self.log.error("open_url: Error: {0}".format(err.code))
            return "open_url: Error: {0}".format(err.code)
        response = res.info()
        res.close()
        if response['content-type'].startswith('audio/') or response['content-type'].startswith('video/'):
            pass
        if response['content-type'].startswith('image/'):
            o = self._getimg(url, response['content-length'])
        elif response['content-type'].startswith('text/'):
            try:
                soup = self._getsoup(url)
                title = self._cleantitle(soup.title.string)
                # bad domains.
                # baddomains = ['twitter.com', 'panoramio.com', 'kickass.to', 'tinypic.com', 'ebay.com', 'imgur.com', 'dropbox.com']
                urlhostname = urlparse(url).hostname
                if __builtins__['any'](b in urlhostname for b in self.baddomains):
                    gd = False
                # check if we should "get description" (GD)
                if gd:
                   # Yes! Get webpage description
                   des = soup.find('meta', attrs={'name': lambda x: x and x.lower()=='description'})
                   if des and des.get('content'):
                       desc = self._cleandesc(des['content'].strip())
                if title:
                    if urlparse(url).hostname not in self.shortUrlServices:
                        shorturl = self._make_tiny(url).replace('http://', '')
                    else:
                        longurl = self._longurl(url).replace('http://', '')
                    o = "{0} - {1}".format(longurl if not shorturl else shorturl, title)
                else:
                    o = None
                if desc:
                    return {'title': o, 'desc': desc}
            except Exception as err:
                return "open_url: Error: {0}".format(err)
                # Non-fatal error traceback information
                self.log.info(traceback.format_exc())
                # or
                # self.log.info(sys.exc_info()[0])
        else:
            # handle any other filetype using libmagic.
            o = self._filetype(url)
        return o

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

    def _bytesto(self, bytes, to, bsize=1024):
        """Convert bytes to megabytes, etc.
           sample code:
               print('mb= ' + str(_bytesto(314575262000000, 'm')))
           sample output: 
               mb= 300002347.946
        """
        import math
        a = {'k' : 1, 'm': 2, 'g' : 3, 't' : 4, 'p' : 5, 'e' : 6 }
        r = float(bytes)
        for i in range(a[to]):
            r = r / bsize

        return math.ceil(float(r))

    # Check for other filetypes using libmagic
    def _filetype(url):
        """Check for unknown filetypes using libmagic."""
        try:
            import magic # python-magic
        except ImportError:
            return "_filetype: ERROR. I did not find python-magic installed. I cannot continue w/o this."

        response = requests.get(url, timeout=4)
        response.close()
        try:
            size = len(response.content)
            typeoffile = magic.from_buffer(response.content)
            return "Content type: {0} - Size: {1}".format(typeoffile, str(self._bytesto(size, 'k')))
        except Exception as e:  # give a detailed error here in the logs.
            self.log.error("ERROR: _filetype: error trying to parse {0} via other (else) :: {1}".format(url, e))
            self.log.error("ERROR: _filetype: no handler for {0} at {1}".format(response.headers['content-type'], url))
            return None

    def _getimg(self, url, size):
        """Displays image information in channel"""
        from io import BytesIO
        
        self.log.info("_getimg: Trying to open: {0}".format(url))

        # try/except with python images.
        try:
            from PIL import Image
        except ImportError: 
            return "_getimg: ERROR. I did not find Pillow installed. I cannot process images w/o this."
        response = requests.get(url, timeout=4)
        response.close()
        try:  # try/except because images can be corrupt.
            img = Image.open(BytesIO(response.content))
        except Exception as err:
            return "_getimg: ERROR: {0} is an invalid image I cannot read :: {1}".format(url, err)
        width, height = img.size
        if img.format == 'GIF':  # check to see if animated.
            try:
                img.seek(1)
                img.seek(0)
                img.format = "Animated GIF"
            except EOFError:
                pass
        return "Image type: {0}  Dimensions: {1}x{2}  Mode: {3}  Size: {4}Kb".format(img.format, \
                width, height, img.mode, str(self._bytesto(size, 'k')))

    # Create TinyURL link.
    def _make_tiny(self, url):
	    request_url = ('http://tinyurl.com/api-create.php?' + 
	        urlencode({'url':url}))
	    with closing(urlopen(request_url)) as response:
	        return response.read().decode('utf-8')

    # Expand shortened link
    def _longurl(self, url):
        """Expand shortened URLs."""
        session = requests.Session()  # so connections are recycled
        resp = session.head(url, allow_redirects=True)
        return resp.url

    # Open the webpage for parsing
    def _getsoup(self, url):
       """Get web page."""
       req = Request(url)
       # Set language for page
       req.add_header('Accept-Language', 'en-us,en;q=0.5')
       response = urlopen(req, timeout=4)
       page = response.read()
       # Close open file
       response.close()
       soup = BeautifulSoup(page, 'lxml')
       return soup

    ############################################
    # MAIN TRIGGER FOR URLS PASTED IN CHANNELS #
    ############################################
    
    def doPrivmsg(self, irc, msg):
        """Monitor channel for URLs"""
        channel = msg.args[0]  # channel, if any.

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
            # for url in matches:
                # url = self._tidyurl(url)  # should we tidy them?
                output = self.open_url(url)
                # now, with gd, we must check what output is.
                if output:  # if we did not get None back.
                    if isinstance(output, dict):  # we have a dict.
                        # output.
                        if 'desc' in output and 'title' in output and output['desc'] is not None and output['title'] is not None:
                            irc.sendMsg(ircmsgs.privmsg(channel, self._bold(self._teal("TITLE: ")) + output['title']))
                            irc.sendMsg(ircmsgs.privmsg(channel, self._bold(self._teal("DESC : ")) + output['desc']))
                        elif 'title' in output and output['title'] is not None:
                            irc.sendMsg(ircmsgs.privmsg(channel, self._bold(self._teal("TITLE: ")) + output['title']))
                    else:  # no desc.
                        irc.sendMsg(ircmsgs.privmsg(channel, self._bold("Response: ") + output))

    def titler(self, irc, msg, args, opturl):
        """<url>

        Public test function for Titler.
        Ex: http://www.google.com
        """

        channel = msg.args[0]

        # main.
        output = self.open_url(opturl)
        # now, with gd, we must check what output is.
        if output:  # if we did not get None back.
            if isinstance(output, dict):  # we have a dict.
                if 'title' in output:  # we got a title back.
                    irc.reply(self._bold("TITLE: ") + output['title'])
                    if 'desc' in output:
                        irc.reply(self._bold("GD: ") + output['desc'])
            else:
                irc.reply("{0}".format(output))

    titler = wrap(titler, [('text')])

Class = Titlerz

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
