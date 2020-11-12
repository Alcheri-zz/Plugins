![Supported Python versions](https://img.shields.io/badge/python-3.4%2C%203.5%2C%203.6%2C%203.7%2C%203.8-blue.svg)
# An alternative to Supybot's PING function.
Returns the ping result of <hostname | ip or IPv6> using Python's shlex library.

Configuring:
===========

* config channel #channel plugins.myping.enable True or False (or On or Off)

Setting up:
==========

* None required.

Using:
=====

[prefix/nick] pings <hostname | Nick | IPv4 or IPv6>

**Note:** [prefix] may be set via 'config reply.whenAddressedBy.chars'
