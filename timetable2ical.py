#!/usr/bin/env python
# coding=utf-8

import requests
import os
import re
from icalendar import Calendar, Event, vText
from datetime import datetime, date
from configparser import ConfigParser
from requests_ntlm import HttpNtlmAuth
from bs4 import BeautifulSoup


def get(user, password):
    url = 'https://stundenplanws.hsr.ch:4434/Service/'
    method_get_timetable = 'Timetable/'
    method_get_period = 'Timeperiod/'
    response = requests.get(url+method_get_timetable, auth=(user, password))
    print(response)


def parse_user_credentials():
    """
        Reads the "auth.cfg" in the current working directory, reads the
        username and password value from it and returns it as a tuple
        (username, password). Raises AssertionError if the file or the
        configurations could not be found.
    """
    config = ConfigParser()
    assert os.path.exists('auth.cfg'), "Missing configurationfile 'auth.cfg'"
    config.read('auth.cfg')

    assert 'authentication' in config, \
        "Missing authentication section in configuration!"
    assert 'username' in config['authentication'], \
        "Missing username in configuration!"
    assert 'password' in config['authentication'], \
        "Missing username in configuration!"

    return (config['authentication']['username'],
            config['authentication']['password'])


def process():
    # Initialize base calendar object
    cal = Calendar()
    cal.add('prodid', '-//timetable2ical//mxm.dk//')
    cal.add('version', '2.0')

    # TODO: for each event....
    event = Event()
    event.add('summary', 'Python meeting about calendaring')
    event.add('dtstart', datetime(2015,9,23,8,0,0))
    event.add('dtend', datetime(2015,9,23,10,0,0))
    event['location'] = vText('Zimmer X (KKL)')
    cal.add_component(event)

    # Write the result
    with open('example.ics', 'wb') as f:
        f.write(cal.to_ical())

# url = 'http://unterricht.hsr.ch'
#url = 'https://unterricht.hsr.ch/MyStudy/TimeTable/Overview'
url = 'https://adfs.hsr.ch/adfs/ls/auth/integrated/?wa=wsignin1.0&wtrealm=https%3a%2f%2funterricht.hsr.ch%2f'
response = requests.get(url)

# Not in HSR network
if response.status_code == 200:
    print("Please connect to the HSR network (VPN or HSR-Secure)!")
    exit()


def signin():
    user, password = parse_user_credentials()
    session = requests.Session()
    session.auth = HttpNtlmAuth('HSR\\'+user, password, session)

    response = session.get('https://adfs.hsr.ch/adfs/ls/auth/integrated/?wa='
                           'wsignin1.0&wtrealm=https://unterricht.hsr.ch/')

    assert response.status_code == 200, "Authentication has failed!"
    html = BeautifulSoup(response.text, "lxml")

    payload = {
        'wa': html.select('input[name="wa"]')[0]['value'],
        'wresult': html.select('input[name="wresult"]')[0]['value'],
    }
    response = session.post('https://unterricht.hsr.ch/', data=payload)
    assert response.status_code == 200, "Authentication has failed!"
    return (response, session)

# startpage, session = signin()
# TODO: parse "Unterrichtszeit" from terminübersicht

# response = session.get("https://unterricht.hsr.ch/MyStudy/TimeTable/Overview")


today = datetime.now()
semester_start = datetime(2015, 9, 14)
semester_end = datetime(2015, 12, 18)

# Abort we are not in a semester period
if today < semester_start or today > semester_end:
    print("There is no fixed timetable available!")
    exit()

startweek = semester_start.isocalendar()[1]
endweek = semester_end.isocalendar()[1]

# html = BeautifulSoup(response.text, "lxml")
html = BeautifulSoup(open('html.html'), "lxml")


for week in range(startweek, endweek+1):
    print(week)


# 1. get current week
# 2. which semester?
# 4. for each week until semesterend
#   ->

{
    "mo" : {
        ""
    }
}
def to_string(element):
    return ' '.join(list(element.stripped_strings))
for tr in html.findAll("tr", {"id": re.compile('Unit[0-9]+')}):
    #print(tr.th.string.strip()) # = 07:05-07:50
    for td in tr.select('td'):
        # Skip empty fields...
        if td.div is not None:
            # print(td['class']) # Day of the week
            children = list(td.div.contents)
            # print(to_string(children[1]))   # Modul name
            # print(to_string(children[9]))   # Dozent
            # print(to_string(children[13]))  # Zimmer
            # print(to_string(children[17]))  # KW 39,41,43,45,47,49,51
