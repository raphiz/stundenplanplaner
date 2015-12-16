from pyconstraints import Problem
from datetime import datetime, time
from timetableplanner import *
import printer
from itertools import groupby
import vcr


my_modules = ['AD1', 'An2I', 'AutoSpr', 'ExEv', 'InfSi1', 'Bsys2', 'LTec', 'RKI', 'WED1']

# with vcr.use_cassette('mocks.yaml'):
(response, session) = signin()
lectures = lecturesTimes(session, my_modules, True)


#  TODO: replace abbrev with module id
def only_teacher(module_name, teacher_id):
    def criteria(lesson):
        if lesson['abbrev'] == module_name and lesson['teacher'] != teacher_id:
            return False
        return True
    return criteria


def min_chance(chance):
    def criteria(lesson):
        if 'chance' not in lesson.keys():
            return True
        if (lesson['chance']*100) < chance:
            return False
        return True
    return criteria


def in_timrange(start_time, end_time):
    end_datetime = datetime.combine(date.today(), end_time)

    def criteria(lesson):
        end_by = datetime.combine(date.today(), lesson['start_time']) + timedelta(minutes=45)
        if lesson['start_time'] < start_time or end_by > end_datetime:
            return False
        return True
    return criteria


def is_filtered(items):
    for aFilter in filters:
        if len(items) != len(filter(aFilter, items)):
            # print("Possible combination removed by filter %s (%s)" %
            #       (aFilter.__name__, [l['name'] for l in items]))
            return True
    return False


filters = [in_timrange(time(7, 0), time(18, 00)), min_chance(30)]
# in_timrange(time(7, 0), time(18, 00)), only_teacher('TKI', 'STH')]
problem = Problem()
for key, lessons in lectures.items():
    # TODO: find a better solution for non-conflicting...
    if key == 'LTec':
        continue

    lectures = [l for l in lessons if l['type'] == 'v']
    exercises = [l for l in lessons if l['type'] == 'u']

    lectures = sorted(lectures, key=lambda l: l['name'])
    exercises = sorted(exercises, key=lambda l: l['name'])

    groups_v = dict((k, list(v)) for k, v in groupby(lectures, lambda l: l['class']))
    groups_u = groupby(exercises, lambda l: l['name'])

    combinations = []
    for k, items in groups_u:
        items = [i for i in items]

        if items[0]['class'] in groups_v.keys():
            items = items + groups_v[items[0]['class']]

        if not is_filtered(items):
            combinations.append(items)
    problem.add_variable(key, combinations)


def unique_timing(*args):
    slots = {'Mon': [], 'Tue': [], 'Wed': [], 'Thu': [], 'Fri': [], 'Sat': [], 'Sun': []}
    for module in args:
        for lesson in module:
            if lesson['start_time'] in slots[lesson['day']]:
                return False
            slots[lesson['day']].append(lesson['start_time'])
    return True


def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    return x > start and x < end


DAYS_OF_THE_WEEK = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']


def free_time(how_often, days, min_start, min_stop):
    # # How often this kind free time shall take place
    # how_often = 1
    #
    # # Which days (here Mon-Fri)
    # days = range(5)
    #
    # # The time in which no lectures shall take place
    # min_start = time(12)
    # min_stop = time(23)

    def criteria(*args):
        slots = [True for x in range(7)]
        for module in args:
            for lesson in module:
                if time_in_range(min_start, min_stop, lesson['start_time']):
                    slots[DAYS_OF_THE_WEEK.index(lesson['day'])] = False

        if len([x for x in slots[days[0]:days[-1]+1] if x]) < how_often:

            return False
        return True
    return criteria

problem.add_constraint(unique_timing, problem._variables.keys())

# One afternoon free - at least twice a week starting at 10
problem.add_constraint(free_time(1, range(5), time(12), time(23)), problem._variables.keys())
problem.add_constraint(free_time(2, range(5), time(6), time(9)), problem._variables.keys())

start = datetime.now()
solutions = problem.get_solutions()
print("Calculation took %s seconds" % (datetime.now() - start).total_seconds())
print("Found %s solutions!" % len(solutions))

nr_timetables_to_print = len(solutions) if len(solutions) < 10 else 10
for i in range(0, nr_timetables_to_print):
    lectures = []
    for val in solutions[i].values():
        lectures += val
    printer.verify(lectures)
    printer.printTimeTable(lectures)
    print('\n')
