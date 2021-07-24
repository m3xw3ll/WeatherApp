import requests
import argparse
import os
import json
from tabulate import tabulate

KEYFILE = 'key.txt'

def degrees_to_cardinal(d):
    '''
    Calculate wind direction

    :param d: Wind degree
    :return: Wind direction as string
    '''

    dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    ix = int((d + 11.25)/22.5)
    return dirs[ix % 16]

def get_weather(apikey, city, lang, units):
    '''
    Get weather information

    :param apikey: API key from https://openweathermap.org
    :param city: The city name
    :param lang: Language in which you want to get the description
                 A list of supported languages can be found at https://openweathermap.org/current#multi
    :param units: Unit of measurement
    :return: a dict containing the weather information
    '''

    r = requests.get('http://api.openweathermap.org/data/2.5/weather?appid={}&q={}&lang={}&units={}'.format(apikey, city, lang, units))
    r = r.json()
    if r['cod'] == '404':
        print(r['message'])
        exit()
    else:
        infodict = {'iconid': r['weather'][0]['id'],
                    'desc': r['weather'][0]['description'],
                    'temp': r['main']['temp'],
                    'pressure': r['main']['pressure'],
                    'humidity': r['main']['humidity'],
                    'windspeed': r['wind']['speed'],
                    'winddeg':r['wind']['deg'],
                    'countryid': r['sys']['country'],
                    'city': r['name']
                    }

        return infodict

def load_data(datapath):
    '''
    Load the icon set and weather codes

    :param datapath: Path to the json file
    :return: The json file
    '''

    with open(datapath, encoding='utf-8') as data:
        jsonData = json.load(data)
        data.close()

        return jsonData

if __name__ == '__main__':

    # Create parser
    parser = argparse.ArgumentParser(description='WeatherApp')
    parser.add_argument('-c', required=True, help='Your City')
    parser.add_argument('-u', choices=['metric', 'imperial'], help='Temperature is available in Fahrenheit, Celcius and Kelvin units.'
                                                                        'For temperature in Fahrenheit use units=imperal'
                                                                        'For temperature in Celcius use units=metric'
                                                                        'Temperature in Kelvin is used by default')
    parser.add_argument('-l', default='en', help='You can use this parameter to get the output in your language')

    args = parser.parse_args()

    # Try to load the API key file and validate it
    try:
        if os.path.getsize(KEYFILE) > 0:
            with open(KEYFILE, 'r') as keyfile:
                apikey = keyfile.read()
        else:
            print("The file is empty. Please add your API key in the file.")
    except OSError as e:
        print(e)
        exit()


    result = get_weather(apikey, args.c, args.l, args.u)
    data = load_data('data.json')

    # find right icon for returned weather code
    for i in data:
        for e in data[i]:
            if result['iconid'] in e['codes']:
                icon = (e['icon'].encode('raw_unicode_escape').decode( 'unicode_escape'))

# format text
winddirection = degrees_to_cardinal(result['winddeg'])
tempunit = '°C' if args.u == 'metric' else '°F' if args.u == 'imperial' else 'K'
col3 = '''
{} {}
{} hPa
{} %
({}) {} km/h
'''.format(str(result['temp']), tempunit, str(result['pressure']), str(result['humidity']), winddirection ,result['windspeed'])


# create and print report
table = [[icon, col3]]
print('\nWeather in city: {}\n{}'.format(result['city'], result['desc']))
print(tabulate(table,tablefmt="plain"))