from planner import AdUnisHSR
from planner import Planner
from planner import utils
from planner import restrictions
from datetime import time
from tabulate import tabulate
import vcr

DAYS_OF_THE_WEEK = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']


def printTimeTable(lectures):
    """
    Utility Method to print timetables
    """
    times = sorted(set(map(lambda l: l['start_time'], lectures)))

    table = [["Time"] + DAYS_OF_THE_WEEK]
    for time in times:
        row = [time]
        for day in DAYS_OF_THE_WEEK:
            res = filter(lambda l: l['start_time'] == time and l['day'] == day, lectures)
            if len(res) > 1:
                row.append('CONFLICT')
            if len(res) == 1:
                row.append(res[0]['name'])
            else:
                row.append('')
        table.append(row)
    print(tabulate(table, headers="firstrow"))


with vcr.use_cassette('fixtures/demo', record_mode='new_episodes'):
    modules = ['MsTe', 'AD2', 'BuRe1', 'CPl', 'MGE', 'SE1', 'WED2']

    source = AdUnisHSR()
    username, password = utils.parse_user_credentials('auth.cfg')
    response = source.signin(username, password)

    filters = [  # Only allow lessons between 7 and 18 o'clock
                  restrictions.InTimeRange(time(7, 0), time(18, 00)),
                 # Minimal required chance - if available
                 restrictions.MinChance(30),
                 # once a week an afternoon off
                 restrictions.FreeTime(3, range(5), time(12), time(23)),
                 # twice a week no module before 9 o'clock
                  restrictions.FreeTime(2, range(5), time(6), time(9))
                ]

    planner = Planner(modules, source)
    solutions = planner.solve(filters)

    # Print max. 10 timetables
    nr_timetables_to_print = len(solutions) if len(solutions) < 10 else 10
    for i in range(0, nr_timetables_to_print):
        lectures = []
        for val in solutions[i].values():
            lectures += val
        # printer.verify(lectures)
        printTimeTable(lectures)
        print('\n')
