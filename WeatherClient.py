import requests
import bs4
import pycountry
import collections


WeatherReport = collections.namedtuple('WeatherReport', 'location,condition, temp, temp_hi, temp_lo, feel, scale')


def main():
    print_header()
    country_code = get_country_code()
    city_code = get_city_code(country_code)
    html = get_html(country_code, city_code)
    report = get_weather_from_html(html)
    print_report(report)


def get_city_code(country_code):
    # get city name and check if website 404s due to invalid city
    code = None
    while code is None or 404:
        code = input("Enter name of City: ")
        status = get_html_status(country_code, code)
        if status == 200:
            return code
        else:
            print("ERROR: Invalid City")


def get_country_code():
    # check if country is valid using pycountry
    code = None
    country_dict = {country.alpha_2: country.name for country in pycountry.countries}
    country_list = [(country.alpha_2, country.name) for country in pycountry.countries]
    while code is None or 'list':
        code = input('Input country code(list for list): ')
        if code == 'list':
            print('++++++COUNTRY LIST++++++\n')
            for country in range(len(country_list)):
                print(country_list[country][0] + ":", country_list[country][1])
            print('++++++++++++++++++++++++\n')
        else:
            try:
                print("You have selected {}.".format(country_dict[code.upper()]))
                return code
            except KeyError:
                print("ERROR: Invalid input")


def get_html(country_code, city_code):
    url = 'http://www.wunderground.com/weather/{}/{}'.format(country_code, city_code)
    response = requests.get(url)
    return response.text


def get_html_status(country_code, city_code):
    url = 'http://www.wunderground.com/weather/{}/{}'.format(country_code, city_code)
    response = requests.get(url)
    return response.status_code


def get_weather_from_html(html):
    # cityCss = '.region-content-header h1'
    # weatherScaleCss = '.wu-unit-temperature .wu-label'
    # weatherTempCss = '.wu-unit-temperature .wu-value'
    # weatherConditionCss = '.condition-icon'
    soup = bs4.BeautifulSoup(html, 'html.parser')
    loc = soup.find(class_='region-content-header').find('h1').get_text().strip()
    condition = soup.find(class_='condition-icon').get_text().strip()
    temp = soup.find(class_='wu-unit-temperature').find(class_='wu-value').get_text().strip()
    scale = soup.find(class_='wu-unit-temperature').find(class_='wu-label').get_text().strip()
    temp_hi = soup.find(class_='condition-data').find(class_='hi').get_text().strip().strip('°')
    temp_lo = soup.find(class_='condition-data').find(class_='lo').get_text().strip().strip('°')
    feel = soup.find(class_='feels-like').find(class_='temp').get_text().strip().strip('°')
    report = WeatherReport(location=loc, condition=condition, temp=convert_to_int(temp), temp_hi=convert_to_int(temp_hi),
                           temp_lo=convert_to_int(temp_lo), feel=convert_to_int(feel), scale=scale)

    return report


def convert_to_int(temp):
    # some countries don't do lows
    try:
        return int(temp)
    except ValueError:
        return temp


def convert_temp(temp, scale):
    # convert fahrenheit to a real unit
    try:
        if scale == 'F':
            temperature = (temp-32)*0.5556
            return format(temperature, '.0f')
        elif scale == 'C':
            return temp
    except TypeError:
        return temp


def print_header():
    print('----------------------------------')
    print('            Weather Client')
    print('----------------------------------')


def print_report(report):
    print('----------------------------------')
    print('Weather Report for: {}'.format(report.location))
    print('Condition: {}'.format(report.condition))
    print('Temperature: {}°C'.format(convert_temp(report.temp, report.scale)))
    print('Feels Like: {}°C'.format(convert_temp(report.feel, report.scale)))
    print('With a high of: {}°C'.format(convert_temp(report.temp_hi, report.scale)))
    print('With a low of: {}°C'.format(convert_temp(report.temp_lo, report.scale)))


if __name__ == '__main__':
    main()
