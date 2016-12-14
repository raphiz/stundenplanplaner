from planner import AdUnisHSR
from planner import Planner
from planner import utils
from planner import restrictions
from datetime import time
import vcr


# with vcr.use_cassette('fixtures/demo_timetables', record_mode='new_episodes'):
module_spec = {'Dbs2': {'v': 2, 'u': 2},
               'BuRe2a': [
                {'abbrev': 'ReVertr', 'v': 2},
                {'abbrev': 'ManagSim', 'u': 2},
                ],
               'InfSi3': {'v': 2, 'u': 2},
               'ParProg': {'v': 2, 'u': 2},
               'PhAI': {'v': 3, 'u': 1},
               'SE2': {'v': 2, 'u': 2},
               'Vss': {'v': 2, 'u': 2},
               'WI1': [
                    {'abbrev': 'ITBus', 'v': 2, 'u': 2}
                ],
               }
source = AdUnisHSR()
username, password = utils.parse_user_credentials('auth.cfg')
response = source.signin(username, password)

filters = [
            # restrictions.InTimeRange(time(7, 0), time(18, 00)),
            # restrictions.MinChance(30),
            # restrictions.FreeTime(1, range(5), time(12), time(23)),
            # restrictions.FreeTime(1, range(5), time(6), time(23))
            restrictions.FreeTime(1, [2], time(17), time(23)),
            restrictions.FreeTime(1, [4], time(7), time(12))
            ]

planner = Planner(module_spec.keys(), source, AdUnisHSR.NEXT_SEMESTER)
solutions = planner.solve(filters)

for solution in solutions:
    planner.verify(module_spec, solution)

# Print max. 10 timetables
nr_timetables_to_print = len(solutions) if len(solutions) < 10 else 10
for i in range(0, nr_timetables_to_print):
    lectures = []
    for val in solutions[i].values():
        lectures += val
    utils.print_time_table(lectures)
    print('\n')
