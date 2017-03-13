# A simple Web Title Snarfer.

This plugin uses TinyURL as an enhancement to output.

Configuring
===========

* Enable/Disable for specific channels: config supybot.plugins.Titlerz.enable True or False (or On or Off
* In channel: [command prefix or BotNick]config channel #channel plugins.titlerz.enable True or False (or On or Off)
              [command prefix] May be set via 'config reply.whenAddressedBy.chars'
* Options   : enable or disable

Setting up
==========

- 1.) Required Python 2 libraries:

    - BeautifulSoup (make a change if you install them locally like I do)
      *  pip install beautifulsoup4 --user --upgrade

- 2.) Required Python parser:
      *  apt-get install python-lxml
      *  easy_install lxml
      *  pip install lxml
      
<p>If you're already using ShrinkURL and Web, disable their overlapping features.</p> <p>/msg <bot> plugins.ShrinkUrl.shrinkSnarfer False<br> /msg <bot> plugins.Web.titleSnarfer False</p> <p>Otherwise, you will have duplicates being pasted. You do not need to unload either and it's <b>not</b> recommended as each has functionality elsewhere in the bot.</p> 

Inspiration: <a target="_new" href="https://github.com/reticulatingspline/Supybot-Titler">Supybot-Titler</a>
