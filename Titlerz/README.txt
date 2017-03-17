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

- 1.) Required Python libraries:

    - BeautifulSoup (make a change if you install them locally.)    
        pip3 install beautifulsoup4 --upgrade
    - future
        pip3 install future
    - Pillow
        pip3 install Pillow

- 2.) Required Python parser:
        apt-get install python-lxml
        easy_install lxml
        pip3 install lxml

If you're already using ShrinkURL and Web, disable their overlapping features.

/msg <bot> plugins.ShrinkUrl.shrinkSnarfer False
/msg <bot> plugins.Web.titleSnarfer False

Otherwise, you will have duplicates being pasted. You do not need to unload either and it's NOT recommended as each has functionality elsewhere in the bot.

* This plugin is Python 2 backwards compatible.

https://github.com/reticulatingspline/Supybot-Titler
