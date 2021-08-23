![Supported Python versions](https://img.shields.io/badge/python-3.4%2C%203.5%2C%203.6%2C%203.7%2C%203.8-blue.svg)
# An alternative to Supybot's DNS function.
Returns the ip of <hostname | URL | nick | IPv4 or IPv6> or the reverse DNS hostname of \<ip\> using Python's socket library.

Configuring:
===========

This plugin uses ipstack to get data. An API (free) key is required.
Get an API key: [ipstack](https://ipstack.com/)

Unload the Internet plugin as it conflicts with this plugin:

Configure your bot:

* /msg yourbot load mydns
* /msg yourbot `config plugins.MyDNS.ipstackAPI your_key_here`
* /msg yourbot unload Internet
* /msg yourbot `config channel #channel plugins.MyDNS.enable True or False` (On or Off)

Setting up:
==========

* This plugin uses Python's HTTP client. If not already installed run the following from the plugins/MyDNS folder.
* `pip install -r requirements.txt` 

Using:
=====

[prefix/nick] dns <hostname | URL | nick | IPv4 or IPv6>

**Note:** [prefix] may be set via `config reply.whenAddressedBy.chars`
