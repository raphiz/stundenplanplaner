from .exceptions import AuthenticationException

import re
from datetime import datetime, date, time, timedelta

import requests
from requests_ntlm import HttpNtlmAuth
from bs4 import BeautifulSoup


class AdUnisHSR:
    HSR_BASE = "http://unterricht.hsr.ch/"
    EXTERNAL_LOGIN_URL = ('https://adfs.hsr.ch/adfs/ls/?wa=wsignin1.0&wtrealm='
                          'https%3a%2f%2funterricht.hsr.ch%2f')
    MODULE_BASE_NEXT = HSR_BASE + "NextSem/TimeTable/Overview/Module"
    # TODO: Test when ready: MODULE_BASE_NEXT = HSR_BASE + "NextSem/TimeTable/Overview/Module"
    MY_TIMETABLE = HSR_BASE + 'NextSem/TimeTable/Overview/Me'

    def __init__(self):
        self.session = requests.Session()
        self.signed_in = False

    def _in_HSR_network(self):
        response = requests.get(self.HSR_BASE)
        return response.status_code == 401

    def signin(self, user, password):
        if self._in_HSR_network():
            self.session.auth = HttpNtlmAuth('HSR\\'+user, password, self.session)

            response = self.session.get('https://adfs.hsr.ch/adfs/ls/auth/integrated/?wa='
                                        'wsignin1.0&wtrealm=https://unterricht.hsr.ch/')

            if not response.status_code == 200:
                raise AuthenticationException(
                    "Authentication has failed (Status code was %s)!" % response.status_code)
        else:
            response = self.session.get(self.EXTERNAL_LOGIN_URL)
            html = BeautifulSoup(response.text, "lxml")
            payload = {'ctl00$ContentPlaceHolder1$UsernameTextBox': user,
                       'ctl00$ContentPlaceHolder1$PasswordTextBox': password,
                       'ctl00$ContentPlaceHolder1$SubmitButton': '',
                       '__db': html.select('input[name="__db"]')[0]['value'],
                       '__VIEWSTATE': html.select('input[name="__VIEWSTATE"]')[0]['value'],
                       '__VIEWSTATEGENERATOR': html.select('input[name="__VIEWSTATEGENERATOR"]')[0]['value'],
                       '__EVENTVALIDATION': html.select('input[name="__EVENTVALIDATION"]')[0]['value'],
                       }
            response = self.session.post(self.EXTERNAL_LOGIN_URL, data=payload)
            if 'set-cookie' not in response.headers.keys():
                raise AuthenticationException("Authentication has failed (Not accepted)!")

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

    def all_modules_ids(self):
        if not self.signed_in:
            raise AuthenticationException("You must log in before you can query!")
        modules = {}
        html = BeautifulSoup(self.session.get(self.MODULE_BASE_NEXT).text, "lxml")
        for option in html.select("option"):
            m = re.search('.*\[M_(.*)\]', option.get_text())
            if m is not None:
                modules[m.group(1)] = option.get('value')
        return modules

    def lectures_times(self, modules, include_availability=False):
        if not self.signed_in:
            raise AuthenticationException("You must log in before you can query!")

        modules_ids = self.all_modules_ids()
        lectures = {}
        headers = {'Referer': 'https://unterricht.hsr.ch/NextSem/TimeTable/Register'}

        for module in modules:
            timetable_url = self.MODULE_BASE_NEXT + '?modId=' + modules_ids[module]
            lectures[module] = self._parse_timetable(self.session.get(timetable_url).text)
            # TODO: Test when available!
            # if include_availability:
            #     av_url = AVAILABILITY_BASE + '?id=' + modules_ids[module]
            #     parse_availability(lectures[module], session.get(av_url, headers=headers).json())
        return lectures

    def _parse_timetable(self, raw):
        soup = BeautifulSoup(raw, "lxml")
        table = soup.find('table', {'id': 'timeTable'})

        rows = table.findAll('tr')
        lessons = []
        p = re.compile(ur'([A-Za-z0-9]+)-(v|u|p|se)([0-9])([0-9]?)')

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
                    mtch = re.match('^KW ([0-9]{1,2}(\,[0-9]{1,2})*).*',
                                    self._to_string(children[17]))
                    lesson['weeks'] = None
                    if mtch is not None:
                        lesson['weeks'] = mtch.groups()[0]
                    time_fragments = time_str.split('-')[0].split(':')
                    lesson['start_time'] = time(hour=int(time_fragments[0]),
                                                minute=int(time_fragments[1]))
                    lessons.append(lesson)
        return lessons

    def _to_string(self, element):
        return ' '.join(list(element.stripped_strings))
