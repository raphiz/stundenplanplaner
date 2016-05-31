import re
from datetime import time

from .exceptions import AuthenticationException
from .exceptions import ScraperException
from .exceptions import DatasourceException

import requests
from requests_ntlm import HttpNtlmAuth
from bs4 import BeautifulSoup


class AdUnisHSR:
    """
    This class provides an API for the HSR AdUnis webportal.

    THE PROGRAM IS DISTRIBUTED IN THE HOPE THAT IT WILL BE USEFUL, BUT WITHOUT ANY WARRANTY!
    """

    CURRENT_SEMESTER = 'CURRENT_SEMESTER'
    NEXT_SEMESTER = 'NEXT_SEMESTER'

    def __init__(self, cache_enabled=True):
        self.scraper = _AdUnisScraper()
        self.cache_enabled = cache_enabled
        self.cache = {}
        self.signed_in = False

    def signin(self, user, password):
        """
        Sign in the given user using the provided password.

        If the authentication fails, a AuthenticationException is thrown

        it is possible, that a ScraperException is thrown. This indicates that
        something has changed on the AdUnis site and the scraper needs to be updated.

        """
        self.scraper.signin(user, password)
        self.signed_in = True

    def modules(self, semester):
        """
        Returns an unordered list of *all* modules in the provided semester.

        Note that the attributes starting with an underscore should not be used since they
        are for internal purpose.

        Example result:
        ```
        [
            {
                'department': u 'EEU',
                '_id': '59791',
                'name': u 'Thermo- und Fluiddynamik 1 (EEU)',
                'id': u 'TFD1EU'
            }, {
                'department': u 'I',
                '_id': '57886',
                'name': u 'Studienarbeit Informatik',
                'id': u 'SAI14'
            }
          [...]
        ]
        ```
        """
        self._require_signin()
        self._validate_semester(semester)

        modules_by_id = self._cached(self.scraper.modules_by_id, semester)
        return modules_by_id.values()

    def students(self, semester):
        """
        Returns an unordered list of *all* students in the provided semester.

        Note that the attributes starting with an underscore should not be used since they
        are for internal purpose.

        Example result:
        ```
        [
          {
              'lastname': u 'Muster',
              '_id': '22222',
              'firstame': u 'Maria',
              'id': u '500000'
          }, {
              'lastname': u 'Meier',
              '_id': '33333',
              'firstame': u 'Hans Felix',
              'id': u '500001'
          }
          [...]
        ]
        ```
        """
        self._require_signin()
        self._validate_semester(semester)

        students_by_id = self._cached(self.scraper.students_by_id, semester)
        return students_by_id.values()

    def subscribed_modules(self, semester):
        self._require_signin()
        # TODO: $('#unregisterForm td > a')

    def subscribable_modules(self, semester):
        self._require_signin()
        # TODO: $('#registerForm td > a')

    def lessons_for_module(self, semester, module_identifier):
        """
        Returns an *unordered* list of all lessons of the given module.

        The module_identifier is the abbrevation of a Module, eg. InfSi1

        Example result:
        ```
        [
          {
              'start_time': datetime.time(10, 10),
              'name': u 'InfSi1-v1',
              'teacher': u 'HEI SFF',
              'day': 'Mon',
              'abbrev': u 'InfSi1',
              'team': u '',
              'weeks': None,
              'type': u 'v',
              'class': u '1',
              'room': u '3.008'
          }, {
              'start_time': datetime.time(11, 5),
              'name': u 'InfSi1-v1',
              'teacher': u 'HEI SFF',
              'day': 'Mon',
              'abbrev': u 'InfSi1',
              'team': u '',
              'weeks': None,
              'type': u 'v',
              'class': u '1',
              'room': u '3.008'
          },
          [...]
        ]
        ```
        """
        self._require_signin()
        self._validate_semester(semester)

        modules_by_id = self._cached(self.scraper.modules_by_id, semester)
        if module_identifier not in modules_by_id.keys():
            raise DatasourceException('Module %s not found!' % module_identifier)

        internal_id = modules_by_id[module_identifier]['_id']
        return self._cached(self.scraper.lectures_times_module, semester, internal_id)

    def lessons_for_student(self, semester, student_identifier):
        """
        Returns an *unordered* list of all lessons of the given module.

        The module_identifier is the abbrevation of a Module, eg. InfSi1

        Example result:
        ```
        [
           {
               'start_time': datetime.time(8, 10),
               'name': u 'AD1-v1',
               'teacher': u 'LET',
               'day': 'Tue',
               'abbrev': u 'AD1',
               'team': u '',
               'weeks': None,
               'type': u 'v',
               'class': u '1',
               'room': u '3.008'
           }, {
               'start_time': datetime.time(8, 10),
               'name': u 'An2I-v2',
               'teacher': u 'AUG',
               'day': 'Wed',
               'abbrev': u 'An2I',
               'team': u '',
               'weeks': None,
               'type': u 'v',
               'class': u '2',
               'room': u '1.207'
          }
          [...]
        ]
        ```
        """
        self._require_signin()
        self._validate_semester(semester)

        students_by_id = self._cached(self.scraper.students_by_id, semester)
        if student_identifier not in students_by_id.keys():
            raise DatasourceException('Student %s not found!' % student_identifier)

        internal_id = students_by_id[student_identifier]['_id']
        return self._cached(self.scraper.lectures_times_student, semester, internal_id)

    def _require_signin(self):
        """
        Simple utility method to ensure that the user is logged in.
        """
        if not self.signed_in:
            raise AuthenticationException('Not signed in!')

    def _validate_semester(self, semester):
        """
        Simple utility method to ensure that the given semester value is valid.
        """
        if semester not in [self.CURRENT_SEMESTER, self.NEXT_SEMESTER]:
            raise DatasourceException('The specified semester value is invalid!')

    def _cached(self, method, *args):
        """
        Call the given method (and store it in the cache if enabled)
        or load the result from the cache (if enabled)
        """
        cache_key = method.__name__ + '-' + '-'.join(args)
        loaded_value = None
        if self.cache_enabled and cache_key in self.cache.keys():
            loaded_value = self.cache[cache_key]
        else:
            loaded_value = method(*args)
            if self.cache_enabled:
                self.cache[cache_key] = loaded_value
        return loaded_value


class _AdUnisScraper:
    """
    This is the part, where the ADUNIS site is parsed directly.
    INTERNAL USE ONLY!
    """

    HSR_BASE_URL = 'https://unterricht.hsr.ch/'
    LOGIN_BASE_URL = 'https://adfs.hsr.ch/adfs/ls/'

    EXTERNAL_LOGIN_URL = LOGIN_BASE_URL + '?wa=wsignin1.0&wtrealm=' + HSR_BASE_URL
    INTERNAL_LOGIN_URL = LOGIN_BASE_URL + '/auth/integrated/?wa=wsignin1.0&wtrealm=' + HSR_BASE_URL

    MODULE_TIMETABLE_URL = HSR_BASE_URL + "%s/TimeTable/Overview/Module"
    STUDENT_TIMETABLE_URL = HSR_BASE_URL + '%s/TimeTable/Overview/Student'

    REGISTER_FORM_URL = HSR_BASE_URL + '%s/TimeTable/Register'

    SEMSTER_PLACEHOLDERS = {
        AdUnisHSR.CURRENT_SEMESTER: 'CurrentSem',
        AdUnisHSR.NEXT_SEMESTER: 'NextSem'
    }

    def __init__(self):
        self.session = requests.Session()

    def _in_HSR_network(self):
        response = requests.get(self.HSR_BASE_URL)
        return response.status_code == 401

    def signin(self, user, password):
        if self._in_HSR_network():
            self.session.auth = HttpNtlmAuth('HSR\\'+user, password, self.session)
            response = self.session.get(self.INTERNAL_LOGIN_URL)

            if not response.status_code == 200:
                raise AuthenticationException("Authentication has failed (Status code was %s)!"
                                              % response.status_code)
        else:
            response = self.session.get(self.EXTERNAL_LOGIN_URL)
            html = BeautifulSoup(response.text, "lxml")
            payload = {
                'ctl00$ContentPlaceHolder1$UsernameTextBox': user,
                'ctl00$ContentPlaceHolder1$PasswordTextBox': password,
                'ctl00$ContentPlaceHolder1$SubmitButton': '',
                '__db': html.select('input[name="__db"]')[0]['value'],
                '__VIEWSTATE': html.select('input[name="__VIEWSTATE"]')[0]['value'],
                '__VIEWSTATEGENERATOR': html.select('[name="__VIEWSTATEGENERATOR"]')[0]['value'],
                '__EVENTVALIDATION': html.select('[name="__EVENTVALIDATION"]')[0]['value']
            }

            response = self.session.post(self.EXTERNAL_LOGIN_URL, data=payload)

            if 'set-cookie' not in response.headers.keys():
                raise AuthenticationException("Authentication has failed (Not accepted)!")

        html = BeautifulSoup(response.text, "lxml")

        payload = {
            'wa': html.select('input[name="wa"]')[0]['value'],
            'wresult': html.select('input[name="wresult"]')[0]['value'],
        }

        response = self.session.post(self.HSR_BASE_URL, data=payload)
        if not response.status_code == 200:
            raise AuthenticationException(
                "Authentication has failed (Status code was %s)!" % response.status_code)
        return response

    def modules_by_id(self, semester):
        url = self.MODULE_TIMETABLE_URL % self.SEMSTER_PLACEHOLDERS[semester]
        html = self._request_page(url)

        modules = {}
        pattern = re.compile('^(.*) \[M_(.*)\] \(([A-Z]*)\)$')
        for option in html.select("#Parameter_ModulId .selectListLevel1"):
            match = pattern.match(option.get_text())
            if match is None:
                raise ScraperException('Failed to parse module name %s' % option.get_text())
            groups = match.groups()
            modules[groups[1]] = {'_id': option.get('value'),
                                  'name': groups[0],
                                  'id': groups[1],
                                  'department': groups[2]}
        return modules

    def students_by_id(self, semester):
        url = self.STUDENT_TIMETABLE_URL % self.SEMSTER_PLACEHOLDERS[semester]
        html = self._request_page(url)

        students = {}
        pattern = re.compile('^([^\,]*), ([^\,]*) \(([0-9]*)\)$')
        for option in html.select("#Parameter_StudentRollenId .selectListLevel1"):
            match = pattern.match(option.get_text())
            if match is None:
                raise ScraperException('Failed to parse student name %s' % option.get_text())
            groups = match.groups()
            students[groups[2]] = {'_id': option.get('value'),
                                   'lastname': groups[0],
                                   'firstame': groups[1],
                                   'id': groups[2]}
        return students

    def lectures_times_module(self, semester, internal_module_id):
        url = self.MODULE_TIMETABLE_URL % self.SEMSTER_PLACEHOLDERS[semester]
        url += '?modId=' + internal_module_id
        html = self._request_page(url)
        return self._parse_timetable(html)

    def lectures_times_student(self, semester, internal_student_id):
        url = url = self.STUDENT_TIMETABLE_URL % self.SEMSTER_PLACEHOLDERS[semester]
        url += '?studId=' + internal_student_id
        html = self._request_page(url)
        return self._parse_timetable(html)

    def _request_page(self, url):
        response = self.session.get(url)
        if response.status_code != 200:
            raise ScraperException('Failed to fetch URL %s (%s)' % (url, response.status_code))
        return BeautifulSoup(response.text, 'lxml')

    def _parse_timetable(self, soup):
        table = soup.find('table', {'id': 'timeTable'})

        rows = table.findAll('tr')
        lessons = []
        p = re.compile(ur'([A-Za-z0-9]+)-([a-z]+)([0-9])([0-9]?)')

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
                    w_match = re.match('^KW ([0-9]{1,2}(\,[0-9]{1,2})*).*',
                                       self._to_string(children[17]))
                    lesson['weeks'] = None
                    if w_match is not None:
                        lesson['weeks'] = w_match.groups()[0]
                    time_fragments = time_str.split('-')[0].split(':')
                    lesson['start_time'] = time(hour=int(time_fragments[0]),
                                                minute=int(time_fragments[1]))
                    lessons.append(lesson)
        return lessons

    def _to_string(self, element):
        return ' '.join(list(element.stripped_strings))
