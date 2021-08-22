###
# Copyright © 2021, Barry Suridge
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###
import re
import requests
import json
import os
import math
from datetime import datetime
try:
    import pgeocode
except ImportError:
    raise callbacks.Error(_('pgeocode is not installed. This plugin will not function!'))

from supybot import callbacks
from supybot.commands import *

# Unicode symbol (https://en.wikipedia.org/wiki/List_of_Unicode_characters#Latin-1_Supplement)
apostrophe = u'\N{APOSTROPHE}'
degree_sign = u'\N{DEGREE SIGN}'
#micro_sign = u'\N{MICRO SIGN}'
percent_sign = u'\N{PERCENT SIGN}'
quotation_mark = u'\N{QUOTATION MARK}'

def contains_number(value):
    numbers = re.findall('[0-9]+', value)
    return True if numbers else False

def dd2dms(longitude, latitude):
    # math.modf() splits whole number and decimal into tuple
    # eg 53.3478 becomes (0.3478, 53)
    split_degx = math.modf(longitude)

    # the whole number [index 1] is the degrees
    degrees_x = int(split_degx[1])

    # multiply the decimal part by 60: 0.3478 * 60 = 20.868
    # split the whole number part of the total as the minutes: 20
    # abs() absolute value - no negative
    minutes_x = abs(int(math.modf(split_degx[0] * 60)[1]))

    # multiply the decimal part of the split above by 60 to get the seconds
    # 0.868 x 60 = 52.08, round excess decimal places to 2 places
    # abs() absolute value - no negative
    seconds_x = abs(round(math.modf(split_degx[0] * 60)[0] * 60,2))

    # repeat for latitude
    split_degy = math.modf(latitude)
    degrees_y = int(split_degy[1])
    minutes_y = abs(int(math.modf(split_degy[0] * 60)[1]))
    seconds_y = abs(round(math.modf(split_degy[0] * 60)[0] * 60,2))

    # account for E/W & N/S
    if degrees_x < 0:
        EorW = 'W'
    else:
        EorW = 'E'

    if degrees_y < 0:
        NorS = 'S'
    else:
        NorS = 'N'

    # abs() remove negative from degrees, was only needed for if-else above
    x = str(abs(degrees_x)) + f'{degree_sign}' + str(minutes_x) + f'{apostrophe} ' + str(seconds_x) + f'{quotation_mark} ' + EorW
    y = str(abs(degrees_y)) + f'{degree_sign}' + str(minutes_y) + f'{apostrophe} ' + str(seconds_y) + f'{quotation_mark} ' + NorS
    return (x, y)

def format_uvi_icon(ico):
    """
    Diplays a coloured icon relevant to the UV Index meter.
    Low: Green Moderate: Yellow High: Orange Very Hight: Red
    Extreme: Violet 🥵
    """
    ico = float(ico)
    if ico >= 0 and ico <= 2.9:
        icon = '🟢'
    elif ico >= 2 and ico <= 5.9:
        icon = '🟡'
    elif ico >= 5 and ico <= 7.9:
        icon = '🟠'
    elif ico >= 7 and ico <= 10.9:
        icon = '🔴'
    else:
        icon = '🟣'
    return icon

def format_weather_output(response):
    """Gather all the data - format it"""
    location  = response['location']
    current   = response['current']

    city_name = location['name']
    region    = location['region']
    country   = location['country']
    cr_date   =  location['localtime']
    cr_date   = datetime.strptime(cr_date, '%Y-%m-%d %H:%M')
    cr_date   = cr_date.strftime("%d-%m-%Y %H:%M")

    # Convert lat, lon data into Degrees Minutes Seconds
    (lon, lat) = dd2dms(int(float(location['lon'])), \
        int(float(location['lat'])))

    description  = current['weather_descriptions']
    atmos        =  current['pressure']
    weather_code = current['weather_code']
    # Get the cloud cover percentage
    cloud        = current['cloudcover']
    # Calculate the direction of the positional arrows
    arrow        = get_wind_direction(current['wind_degree'])
    precip = current['precip']
    if precip:
        precipico = '☔'
    else:
        precipico = ''
    humidity   = current['humidity']
    temp       = current['temperature']
    feelslike  = current['feelslike']
    wind       = current['wind_speed']
    uvi        = current['uv_index']
    utc        = location['utc_offset']
    visibility = response['current']['visibility']
    # Get a weather_code from Weatherstack
    status_icon = get_status_icon(weather_code)
    uvi_icon    = format_uvi_icon(uvi)

    # Remove brackets and single quote marks from 'weather_descriptions'
    description = re.sub('[\'\]\[]', '', str(description))

    # Format output
    a = f'🏠 {city_name} {region} {country} :: Lat {lat} Lon {lon} :: UTC {utc} :: {cr_date} :: {status_icon} {description} '
    b = f'| 🌡 Barometric {atmos}hPa | ☁ Cloud cover {cloud}{percent_sign} | {precipico} Precip {precip}mmh '
    c = f'| 💦 Humidity {humidity}{percent_sign} | Current {temp}°C '
    d = f'| Feels like {feelslike}°C | 🍃 Wind {wind}Km/H {arrow} '
    e = f'| 👁 Visibility {visibility}Km | {uvi_icon} UVI {uvi}'

    s = ''
    seq = [a, b, c, d, e]
    return((s.join( seq )))
#XXX unused
def get_cloud_coverage(cloud_dict):
    if 'all' in cloud_dict:
        clouds = cloud_dict['all']
    else:
        clouds = 0
    return clouds

# Select the appropriate weather status icon
def get_status_icon(code):
    """Use the given code to attach appropriate
    weather status icon"""
    code = str(code)
    switcher = {
        '113': '☀',
        '116': '🌤',
        '119': '☁',
        '122': '☁',
        '143': '🌫',
        '176': '🌧',
        '296': '🌧',
        '302': '🌧',
        '329': '❄',
        '353': '🌧',
        '356': '🌧',
        '371': '❄',
    }
    return switcher.get(code, '🤷')

def get_wind_direction(wind):
    num = wind
    val = int((num/22.5)+.5)
    # Wind direction decoration output
    arr = ['↑ N','NNE','↗ NE','ENE','→ E','ESE', '↘ SE', 'SSE','↓ S','SSW','↙ SW', \
        'WSW','← W','WNW','↖ NW','NNW']
    return arr[(val % 16)]

#XXX unused: Get precipitation reading
def get_rain_precipitation(rain_dict):
    if '1h' in rain_dict:
        rain = rain_dict['1h']
    else:
        rain = 0
    return rain

def query_postal_code(code):
    """This function returns longitude and latitude from
    a postcode."""
    postcode = code.split(',', 1)[0]
    try:
        countrycode = re.sub('[ ]', '', code.split(',', 1)[1])
    except IndexError:
        raise callbacks.Error(_('<postcode, country code>'))
    try:
        nomi = pgeocode.Nominatim(countrycode)
    except ValueError:
        raise callbacks.Error(_(f'{countrycode} is not a known country code.'))
    zip = nomi.query_postal_code(postcode)
    return[zip.latitude, zip.longitude]

class Weatherstack(callbacks.Plugin):
    """A simple OpenWeather plugin for Limnoria"""
    threaded = True

    def __init__(self, irc):

        self.__parent = super(Weatherstack, self)
        self.__parent.__init__(irc)

    def get_address_by_location(self, latitude, longitude):
        """This function returns an address from a location.
        """
        apikey = self.registryValue('positionstackAPI')
        # Missing API Key.
        if not apikey:
            raise callbacks.Error(_( \
                'Please configure the positionstack API key in config plugins.Weatherstack.positionstackAPI'))
        coordinates = f"{latitude}, {longitude}"
        params = {
            'access_key': apikey,
            'query': coordinates,
            'limit': '1'
        }
        r = requests.get('http://api.positionstack.com/v1/reverse', params)
        responses = r.json()
        try:
            locality = responses['data'][0].get('locality')
        except KeyError:
            raise callbacks.Error(_('404: city not found'))
        if str(locality) == 'None':
            raise callbacks.Error(_('404: city not found'))
        return (locality)

    @wrap(['text'])
    def ws(self, irc, msg, args, address):
        """ [<city> <country code or country>] ][<postcode, country code>]
        Get weather information for a town or city.
        I.E. weather Ballarat or Ballarat, AU/Australia OR 3350, AU
        """
        channel = msg.channel

        apikey = self.registryValue('weatherstackAPI')
        # Missing API Key.
        if not apikey:
            raise callbacks.Error(_( \
                'Please configure the Weatherstack API key in config plugins.Weatherstack.weatherstackAPI'))

        # Not 'enabled' in #channel.
        if not self.registryValue('enable', channel):
            return

        # Check if 'address' is a postcode.
        if contains_number(address):
            (lat, lon) = query_postal_code(address)
            address = self.get_address_by_location(lat, lon)

        # Initialise API data
        params = {
            'access_key': apikey,
            'query': address,
            'units': 'm'
        }

        api_result = requests.get('http://api.weatherstack.com/current', params)

        # HTTP Status OK
        if api_result.status_code == 200:
            api_response = api_result.json()  # Data collection
            _status = api_response['current']['weather_descriptions']
            _weather_code = api_response['current']['weather_code']
            # Print the weather output
            irc.reply(format_weather_output(api_response))
        else:
            raise callbacks.Error(_(f'{api_result.status_code} in the HTTP request'))

        # temp weather code collection
        entry = {'status': _status, 'code': _weather_code}
        a = []
        if not os.path.isfile('data.json'):
            a.append(entry)
            with open('data.json', mode='w') as f:
                f.write(json.dumps(a, indent=2))
        else:
            with open('data.json') as feedsjson:
                feeds = json.load(feedsjson)
            feeds.append(entry)
            with open('data.json', mode='w') as f:
                f.write(json.dumps(feeds, indent=2))

    @wrap(['something'])
    def help(self, irc):
        """No help for you as yet """

Class = Weatherstack

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
