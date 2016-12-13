import os

from datetime import datetime, date, timedelta, time

from configparser import ConfigParser
from tabulate import tabulate
from isoweek import Week
from icalendar import Calendar, Event, vText


DAYS_OF_THE_WEEK = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']


def parse_user_credentials(path):
    """
        Reads the username and password value from the cfg-file of
        the give path and returns it as a tuple
        (username, password). Raises AssertionError if the file or the
        configurations could not be found.
    """
    config = ConfigParser()
    assert os.path.exists(path), "Missing configurationfile 'auth.cfg'"
    config.read(path)

    assert 'authentication' in config, \
        "Missing authentication section in configuration!"
    assert 'username' in config['authentication'], \
        "Missing username in configuration!"
    assert 'password' in config['authentication'], \
        "Missing username in configuration!"

    return (config['authentication']['username'],
            config['authentication']['password'])


def time_slots():
    """
    Returns all start times of the available slots
    """
    break_durations = [20, 10, 20, 10, 20, 15, 10, 20, 10, 10, 10, 30, 10]
    first_slot = time(7, 5)
    lesson_duration = 45

    def me(slots, break_duration):
        previous_dtime = datetime.combine(date.today(), slots[-1])
        current_dtime = previous_dtime + timedelta(minutes=break_duration + lesson_duration)
        slots.append(current_dtime.time())
        return slots

    return reduce(me, break_durations, [first_slot])


def print_time_table(lectures):
    """
    Utility Method to print timetables
    """

    table = [["Time"] + DAYS_OF_THE_WEEK]
    for current_time in time_slots():
        row = [current_time]
        for day in DAYS_OF_THE_WEEK:
            res = filter(lambda l: l['start_time'] == current_time and l['day'] == day, lectures)
            if len(res) > 1:
                row.append('CONFLICT')
            if len(res) == 1:
                if res[0]['weeks']:
                    row.append(res[0]['name'] + '\n' + res[0]['weeks'])
                else:
                    row.append(res[0]['name'])
            else:
                row.append('')
        table.append(row)
    print(tabulate(table, headers="firstrow"))
    for lecture in lectures:
        if lecture['weeks'] is not None:
            print("WARNING: Lesson %s is only in KW %s" % (lecture['name'], lecture['weeks']))


def export_to_ical(destination, lessons, start=None, end=None, year=None, weeks=None):
    """
    Export the given lessons to ical for the given year and week or start and end date.

    The destination must be the path to the ical file to writer.

    lessons must be in the same format as returned by AdUnisHSR.

    Weeks must be an iterable returning the KW number(int) (eg. 44, 45, 46)
    """

    if start is not None and end is not None:
        weeks = range(Week.withdate(start).week, Week.withdate(end).week+1)
        year = start.year
    elif not (weeks is not None and year is not None):
        raise TimeTableException('You must either provide a week and a year or start and end date')

    cal = Calendar()
    cal.add('prodid', '-//timetable2ical//mxm.dk//')
    cal.add('version', '2.0')

    for week in weeks:
        reference = datetime.combine(Week(year, week).monday(), time.min)
        # TODO: KWs!
        for lesson in lessons:
            event = Event()
            # print(lesson)
            start = reference + timedelta(
                days=DAYS_OF_THE_WEEK.index(lesson['day']),
                hours=lesson['start_time'].hour,
                minutes=lesson['start_time'].minute)
            end = start + timedelta(minutes=45)
            event.add('summary', "%s (%s)" % (lesson['name'], lesson['teacher']))
            event.add('dtstart', start)
            event.add('dtend', end)
            event.add('categories', lesson['abbrev'])
            cal.add_component(event)

    with open(destination, 'wb') as f:
        f.write(cal.to_ical())
