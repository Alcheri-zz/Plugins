![Supported Python versions](https://img.shields.io/badge/python-3.4%2C%203.5%2C%203.6%2C%203.8-blue.svg)
# An alternative to Supybot's DNS function.
Returns the ip of <hostname | URL | nick | ip or IPv6> or the reverse DNS hostname of \<ip\> using Python's socket library.

Configuring:
===========

** None required.

Setting up:
==========

* Required Python libraries:
    - future
    * pip3 install future
- Or use pip if this points to your Py3 environment.

Using:
=====

[prefix/nick] dns <hostname | URL | nick | ip or IPv6>

**Note:** [prefix] may be set via 'config reply.whenAddressedBy.chars'
