from requests_ntlm import HttpNtlmAuth
import requests
from bs4 import BeautifulSoup
import re
from exceptions import AuthenticationException
from datetime import datetime, date, time, timedelta


class AdUnisHSR:

    HSR_BASE = "http://unterricht.hsr.ch/"
    MODULE_BASE_CURRENT = HSR_BASE + "CurrentSem/TimeTable/Overview/Module"
    MODULE_BASE_NEXT = HSR_BASE + "NextSem/TimeTable/Overview/Module"
    MY_TIMETABLE = HSR_BASE + 'CurrentSem/TimeTable/Overview/Me'

    def __init__(self):
        self.session = requests.Session()
        self.signed_in = False

    def _in_HSR_network(self):
        response = requests.get('https://adfs.hsr.ch/adfs/ls/auth/integrated/?wa=wsignin1.0')
        # TODO: This check does not work
        return response.status_code == 200 or response.status_code == 401

    def signin(self, user, password):
        if not self._in_HSR_network():
            raise AuthenticationException("You must be in the HSR Network!")

        self.session.auth = HttpNtlmAuth('HSR\\'+user, password, self.session)

        response = self.session.get('https://adfs.hsr.ch/adfs/ls/auth/integrated/?wa='
                                    'wsignin1.0&wtrealm=https://unterricht.hsr.ch/')

        if not response.status_code == 200:
            raise AuthenticationException(
                "Authentication has failed (Status code was %s)!" % response.status_code)

        html = BeautifulSoup(response.text, "lxml")

        payload = {
            'wa': html.select('input[name="wa"]')[0]['value'],
            'wresult': html.select('input[name="wresult"]')[0]['value'],
        }
        response = self.session.post('https://unterricht.hsr.ch/', data=payload)
        if not response.status_code == 200:
            raise AuthenticationException(
                "Authentication has failed (Status code was %s)!" % response.status_code)
        self.signed_in = True
        return response

    def all_modules(self):
        if not self.signed_in:
            raise AuthenticationException("You must log in before you can query!")
        modules = {}
        # TODO: current vs next semester?
        html = BeautifulSoup(self.session.get(self.MODULE_BASE_CURRENT).text, "lxml")
        for option in html.select("option"):
            m = re.search('.*\[M_(.*)\]', option.get_text())
            if m is not None:
                modules[m.group(1)] = option.get('value')
        return modules

    #### BEGINLEGACY #######
    def current_timetable(self):
        response = self.session.get(self.MY_TIMETABLE)
        return self._parse_timetable(response.text)

    def _to_string(self, element):
        return ' '.join(list(element.stripped_strings))

    def _parse_timetable(self, raw):
        soup = BeautifulSoup(raw, "lxml")
        table = soup.find('table', {'id': 'timeTable'})

        rows = table.findAll('tr')
        lessons = []
        p = re.compile(ur'([A-Za-z0-9]+)-(v|u)([0-9])([0-9]?)')

        for cell in rows[1:]:
            time_str = cell.th.string.strip()
            for td in cell.select('td'):
                # Skip empty fields...
                for div in td.findAll('div'):
                    lesson = {}
                    lesson['day'] = td['class'][0]

                    children = list(div.contents)
                    lesson['name'] = self._to_string(children[1])
                    match = p.match(lesson['name'])
                    # Module Abbrev - can differ from the module id
                    lesson['abbrev'] = match.group(1)
                    lesson['type'] = match.group(2)
                    lesson['class'] = match.group(3)
                    lesson['team'] = match.group(4)

                    lesson['teacher'] = self._to_string(children[9])  # Dozent
                    lesson['room'] = self._to_string(children[13])    # Zimmer
                    lesson['weeks'] = self._to_string(children[17])   # KW 39,41,43,45,47,49,51
                    time_fragments = time_str.split('-')[0].split(':')
                    lesson['start_time'] = time(hour=int(time_fragments[0]),
                                                minute=int(time_fragments[1]))
                    lessons.append(lesson)
        return lessons
#### END #######
