![Supported Python versions](https://img.shields.io/badge/python-3.6%2C%203.7%2C%203.8%2C%203.9-blue.svg)
# Weather

A plugin for Limnoria that uses the OpenWeather API. All output is in Metric.
This plugin uses Alpha-2 Code for country code [iso.org](https://www.iso.org/obp/ui#iso:pub:PUB500001:en)

Configuring:
===========

This plugin uses Open Weather to get data. A free API key is required.
Get an API key: [OpenWeather](https://openweathermap.org/)

Setting up:
==========

* The following library is required. Run the command (below) from the Weather folder to install.
* requests-cache: A persistent HTTP cache for the python requests library.
* 'pip3 install -r requirements.txt'

Configure your bot:
==================

* '/msg yourbot load Weather'
* '/msg yourbot `config plugins.Weather.openweatherAPI your_key_here`'
* '/msg yourbot config channel #channel plugins.Weather.enable True or False (or On or Off)'

Using:
=====

[prefix/nick] weather [<city> <(Alpha-2) country code>] [<postcode, (Alpha-2) country code>]
 
[prefix/nick] lookup  [<city> <(Alpha-2) country code>]

**Note:** [prefix] may be set via 'config reply.whenAddressedBy.chars'
