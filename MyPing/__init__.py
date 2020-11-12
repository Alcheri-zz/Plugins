###
# Copyright (c) 2020, Barry Suridge
# All rights reserved.
#
#
###

"""
MyPing: An alternative to Supybot's Ping function.
"""

import sys
# Python 3 ONLY!!
if sys.version_info[0] < 3:
    raise RuntimeError("This plugin requires Python 3.")

import supybot
import supybot.world as world

# Use this for the version of this plugin.  You may wish to put a CVS keyword
# in here if you're keeping the plugin in CVS or some similar system.
__version__ = '1.0.1'

# XXX Replace this with an appropriate author or supybot.Author instance.
__author__ = 'Barry Suridge'

# This is a dictionary mapping supybot.Author instances to lists of
# contributions.
__contributors__ = {}

# This is a url where the most recent plugin package can be downloaded.
__url__ = 'https://github.com/Alcheri/Plugins.git'

from . import config
from . import plugin
if sys.version_info >= (3, 4):
    from importlib import reload
else:
    from imp import reload
# In case we're being reloaded.
reload(config)
reload(plugin)
# Add more reloads here if you add third-party modules and want them to be
# reloaded when this plugin is reloaded.  Don't forget to import them as well!

if world.testing:
    from . import test

Class = plugin.Class
configure = config.configure


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
