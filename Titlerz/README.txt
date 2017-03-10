A simple Python test plugin for Limnoria bot.

This plugin uses TinyURL as an enhancement to output.

Configuring
===========

* Enable/Disable for specific channels: config supybot.plugins.Titlerz.enable True or False (or On or Off
* In channel: [command prefixor BotNick]config channel #channel plugins.titlerz.enable True or False (or On or Off)
              [command prefix] May be set via 'config reply.whenAddressedBy.chars'
* Options   : enable or disable

Setting up
==========

- 1.) Required Python 2 libraries:

    - BeautifulSoup (make a change if you install them locally.)    
        pip install beautifulsoup4 --user --upgrade

- 2.) Required Python parser:
        apt-get install python-lxml
        easy_install lxml
        pip install lxml

https://github.com/reticulatingspline/Supybot-Titler
