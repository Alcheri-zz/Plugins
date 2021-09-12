![Python versions](https://img.shields.io/badge/Python-version-blue) ![](https://img.shields.io/badge/3.5%2C%203.6%2C%203.7%2C%203.8%2C%203.9-blue.svg)
# An alternative to Supybots' PING function.
Returns the ping result of <hostname | ip or IPv6> using Python's shlex library.

Configuring:
===========

* `config channel #channel plugins.MyPing.enable True or False` (On or Off)

Setting up:
==========

To stop conflict with Supybots' core 'ping' function do the following:\
`[prefix] defaultplugin --remove ping Misc`\
`[prefix] defaultplugin ping MyPing`

Using:
=====

[prefix/nick] ping <hostname | Nick | IPv4 or IPv6>

**Note:** [prefix] may be set via `config reply.whenAddressedBy.chars`
