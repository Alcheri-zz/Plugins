# DNS

An alternative to Supybot's DNS function.
Returns the ip of <hostname | nick | URL | ip or IPv6> or the reverse DNS hostname of <ip> using Python's socket library.

This plugin uses ipstack to get data. An API (free) key is required.
Get an API key. [ipstack](https://ipstack.com/)

Configure your bot: `/msg yourbot config plugins.MyDNS.apikeys.ipstack API-KEY`
