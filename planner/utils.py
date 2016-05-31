from configparser import ConfigParser
import os
from tabulate import tabulate
from datetime import time

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
    times = []
    current_time = time(7, 5)
    while current_time < time(21):
        times.append(current_time)
        current_time = time(current_time.hour+1, (5 if current_time.minute == 10 and not current_time.hour == 12 else 10))
    return times


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
