# A simple Web Title Snarfer.

Configure plugin for bitly URL services (if needed):

* /msg <bot> config plugins.Titlerz.bitlyLogin <user_name>
* /msg <bot> config plugins.Titlerz.bitlyApiKey <api_key>
* /msg <bot> config plugins.Titlerz.bitlyToken <access_token>

Setting up
==========

- 1.) Required Python 2 libraries:

    - python-magic, Pillow, requests, bs4 (make a change if you install them locally like I do)

      *  pip install python-magic --user --upgrade
      *  pip install Pillow --user --upgrade
      *  pip install requests --user --upgrade
      *  pip install beautifulsoup4 --user --upgrade
      *  pyshorteners >> https://github.com/ellisonleao/pyshorteners
      *  pip install pyshorteners --user --upgrade

- 2.) Required Python parser:
      *  apt-get install python-lxml
      *  easy_install lxml
      *  pip install lxml
