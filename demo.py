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
            print("WARNING: Lesson %s is only in KW %s" % (lecutre['name'], lecture['weeks']))


with vcr.use_cassette('fixtures/demo', record_mode='new_episodes'):
    module_spec = {'MsTe': {'v': 2, 'u': 2},
                   'AD2': {'v': 2, 'u': 2},
                   'BuRe1': [
                    {'abbrev': 'ReIng', 'v': 2},
                    {'abbrev': 'BuPl', 'v': 1, 'u': 1},
                   ],
                   'CPl': {'v': 2, 'u': 2},
                   'MGE': {'v': 2, 'u': 2},
                   'SE1': {'v': 2, 'u': 2},
                   'WED2': {'v': 2, 'u': 2},
                   'PrFm': {'v': 2, 'u': 2}
                   }

    source = AdUnisHSR()
    username, password = utils.parse_user_credentials('auth.cfg')
    response = source.signin(username, password)

    filters = [
                restrictions.InTimeRange(time(7, 0), time(18, 00)),
                restrictions.MinChance(30),
                restrictions.FreeTime(3, range(5), time(12), time(23)),
                # restrictions.FreeTime(1, range(5), time(6), time(23))
                ]

    planner = Planner(module_spec.keys(), source)
    solutions = planner.solve(filters)

    for solution in solutions:
        planner.verify(module_spec, solution)

    # Print max. 10 timetables
    nr_timetables_to_print = len(solutions) if len(solutions) < 10 else 10
    for i in range(0, nr_timetables_to_print):
        lectures = []
        for val in solutions[i].values():
            lectures += val
        # printer.verify(lectures)
        printTimeTable(lectures)
        print('\n')
