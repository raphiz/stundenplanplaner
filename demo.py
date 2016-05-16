from planner import AdUnisHSR
from planner import Planner
from planner import utils
from planner import constraints
from datetime import time
from tabulate import tabulate
import vcr

DAYS_OF_THE_WEEK = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']


def printTimeTable(lectures):
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


with vcr.use_cassette('fixtures/demo'):
    modules = ['AD1', 'An2I', 'AutoSpr', 'ExEv', 'InfSi1', 'Bsys2', 'RKI', 'WED1']

    source = AdUnisHSR()
    username, password = utils.parse_user_credentials('auth.cfg')
    response = source.signin(username, password)

    # TODO: "Merge" the concept of filters and user_constraints - for an easier API
    filters = [ # Only allow lessons between 7 and 18 o'clock
                constraints.in_timrange(time(7, 0), time(18, 00)),
                # Minimal required chance - if available
                constraints.min_chance(30)]

    user_constraints = [ # once a week an afternoon off
                        constraints.free_time(1, range(5), time(12), time(23)),
                        # twice a week no module before 9 o'clock
                        constraints.free_time(2, range(5), time(6), time(9))]

    planner = Planner(modules, source)
    solutions = planner.solve(filters, user_constraints)
    nr_timetables_to_print = len(solutions) if len(solutions) < 10 else 10
    for i in range(0, nr_timetables_to_print):
        lectures = []
        for val in solutions[i].values():
            lectures += val
        # printer.verify(lectures)
        printTimeTable(lectures)
        print('\n')
