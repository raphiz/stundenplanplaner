from pyconstraints import Problem
from datetime import datetime
from itertools import groupby


class Planner:

    def __init__(self, modules, backend):
        """
        Note, that the given backend must be initialized (eg. user must be logged in)
        """
        self.modules = modules
        self.backend = backend
        self.initialized = False

    def _initialize(self):
        """
        Loads the data from the backend and caches the data required for
        calculating a Timetable combination.
        """
        self.lectures = self.backend.lectures_times(self.modules, True)
        self.initialized = True

    def solve(self, filters, constraints):
        """
        Calculates all possible timetable calculations for the given modules
        and the given constraints.
        """
        if not self.initialized:
            self._initialize()

        problem = Problem()
        for key, lessons in self.lectures.items():

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

                if not self._is_filtered(filters, items):
                    combinations.append(items)
            problem.add_variable(key, combinations)

        problem.add_constraint(self._unique_timing, problem._variables.keys())

        # One afternoon free - at least twice a week starting at 10
        for constraint in constraints:
            problem.add_constraint(constraint, problem._variables.keys())

        start = datetime.now()
        solutions = problem.get_solutions()
        print("Calculation took %s seconds" % (datetime.now() - start).total_seconds())
        print("Found %s solutions!" % len(solutions))
        return solutions

    def _is_filtered(self, filters, items):
        for current in filters:
            if len(items) != len(filter(current, items)):
                print("Possible combination removed by filter %s (%s)" %
                      (current.__name__, [l['name'] for l in items]))
                return True
        return False

    def _unique_timing(self, *args):
        slots = {'Mon': [], 'Tue': [], 'Wed': [], 'Thu': [], 'Fri': [], 'Sat': [], 'Sun': []}
        for module in args:
            for lesson in module:
                if lesson['start_time'] in slots[lesson['day']]:
                    return False
                slots[lesson['day']].append(lesson['start_time'])
        return True
