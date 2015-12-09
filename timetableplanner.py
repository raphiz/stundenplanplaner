#!/usr/bin/env python
# coding=utf-8

import requests
import os
import re
from icalendar import Calendar, Event, vText
from datetime import datetime, date, time, timedelta
from configparser import ConfigParser
from requests_ntlm import HttpNtlmAuth
from bs4 import BeautifulSoup


HSR_BASE = "http://unterricht.hsr.ch/"
MODULE_BASE = HSR_BASE + "NextSem/TimeTable/Overview/Module"
DAYS_OF_THE_WEEK = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']


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


def module_list(session):
    modules = {}
    html = BeautifulSoup(session.get(MODULE_BASE).text, "lxml")
    for option in html.select("option"):
        m = re.search('.*\[M_(.*)\]', option.get_text())
        if m is not None:
            modules[m.group(1)] = option.get('value')
    return modules


def in_HSR_network():
    url = 'https://adfs.hsr.ch/adfs/ls/auth/integrated/?wa=wsignin1.0'
    response = requests.get(url)
    return response.status_code == 200


def to_string(element):
    return ' '.join(list(element.stripped_strings))


def parse_timetable(raw):
    soup = BeautifulSoup(raw, "lxml")
    table = soup.find('table', {'id': 'timeTable'})

    rows = table.findAll('tr')
    lessons = []
    for cell in rows[1:]:
        time = cell.th.string.strip()
        for td in cell.select('td'):
            # Skip empty fields...
            for div in td.findAll('div'):
                lesson = {}
                lesson['day'] = td['class'][0]  # Day of the week

                children = list(div.contents)
                lesson['name'] = to_string(children[1])     # Modul name
                lesson['teacher'] = to_string(children[9])  # Dozent
                lesson['room'] = to_string(children[13])    # Zimmer
                lesson['weeks'] = to_string(children[17])   # KW 39,41,43,45,47,49,51
                lesson['time'] = time
                lessons.append(lesson)
    return lessons


def write_planner(lectures, filename):
    cal = Calendar()
    cal.add('prodid', '-//timetable2ical//mxm.dk//')
    cal.add('version', '2.0')

    # This weeks monday as reference
    reference = date.today()
    reference = datetime.combine(reference, time.min) - timedelta(days=reference.weekday())

    for (module, lessons) in lectures.items():
        for lesson in lessons:

            event = Event()
            time_fragments = lesson['time'].split('-')[0].split(':')
            start = reference + timedelta(
                days=DAYS_OF_THE_WEEK.index(lesson['day']),
                hours=int(time_fragments[0]),
                minutes=int(time_fragments[1]))
            end = start + timedelta(minutes=45)

            event.add('summary', "%s (%s) %s" % (lesson['name'], lesson['teacher'], lesson['weeks']))
            event.add('dtstart', start)
            event.add('dtend', end)
            event.add('categories', module)
            cal.add_component(event)

    # Write the result
    with open(filename, 'wb') as f:
        f.write(cal.to_ical())


if __name__ == "__main__":
    my_modules = ['AD1', 'An2I', 'AutoSpr', 'ExEv', 'InfSi1', 'KommIng2', 'LTec', 'RKI', 'WED1']
    (response, session) = signin()
    all_modules = module_list(session)
    lectures = {}
    for module in my_modules:
        url = MODULE_BASE + '?modId=' + all_modules[module]
        lectures[module] = parse_timetable(session.get(url).text)

    write_planner(lectures, 'modules.ics')
