from pyconstraints import Problem
from datetime import datetime
from itertools import groupby, product


class Planner:

    def __init__(self, modules, backend, semester):
        """
        Note, that the given backend must be initialized (eg. user must be logged in)
        """
        self.modules = modules
        self.backend = backend
        self.semester = semester
        self.initialized = False

    def _initialize(self):
        """
        Loads the data from the backend and caches the data required for
        calculating a Timetable combination.
        """
        self.lectures = {}
        for module in self.modules:
            self.lectures[module] = self.backend.lessons_for_module(self.semester, module)
        self.initialized = True

    def solve(self, restrictions):
        """
        Calculates all possible timetable calculations for the given modules
        and the given restrictions.
        """
        if not self.initialized:
            self._initialize()

        problem = Problem()
        for key, module_lessons in self.lectures.items():
            module_lessons = sorted(module_lessons, key=lambda l: l['abbrev'])
            sub_lectures = groupby(module_lessons, lambda l: l['abbrev'])
            for abbrev, lessons in sub_lectures:
                lessons = sorted(lessons, key=lambda l: l['class'])
                combinations = []
                for classnr, cls_lessons in groupby(lessons, lambda l: l['class']):
                    cls_lessons = sorted(cls_lessons, key=lambda l: l['type'])

                    temporary_combinations = []

                    grouped_by_type = [list(v) for k, v in groupby(cls_lessons, lambda l: l['type'])]
                    if len(grouped_by_type) == 1:
                        for g in grouped_by_type:
                            combinations.append(g)
                        continue
                    for lessons_by_type in grouped_by_type:
                        lessons_by_type = sorted(lessons_by_type, key=lambda l: l['team'])
                        u_or_v = []
                        for _, lessons_by_team in groupby(lessons_by_type, lambda l: l['team']):
                            u_or_v.append([l for l in lessons_by_team])

                        if len(temporary_combinations) == 0:
                            temporary_combinations = [u_or_v]
                        else:
                            for combi in temporary_combinations:
                                for x in combi:
                                    for y in u_or_v:
                                        combinations.append(x+y)

                problem.add_variable(abbrev, combinations)

        problem.add_constraint(self._unique_timing, problem._variables.keys())
        for restriction in restrictions:
            if restriction.is_constraint:
                problem.add_constraint(restriction.constraint, problem._variables.keys())

        start = datetime.now()
        solutions = problem.get_solutions()
        print("Calculation took %s seconds" % (datetime.now() - start).total_seconds())
        print("Found %s solutions!" % len(solutions))
        return solutions

    def _is_filtered(self, restrictions, items):
        for restriction in restrictions:
            if not restriction.is_filter:
                return False
            if len(items) != len(filter(restriction.filter, items)):
                print("Possible combination removed by filter \"%s\" (%s)" %
                      (restriction, [l['name'] for l in items]))
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

    def verify(self, specs, modules_by_type):
        for name, spec in specs.items():
            if type(spec) == list:
                for u_spec in spec:
                    if 'abbrev' not in u_spec.keys():
                        raise Exception("abbrev in Module spec for %s not defined!" % (name))
                    self._verify_module(u_spec, modules_by_type)
            else:
                if 'abbrev' not in spec.keys():
                    spec['abbrev'] = name
                self._verify_module(spec, modules_by_type)

    def _verify_module(self, spec, modules_by_type):
        abbrev = spec.pop('abbrev')
        for module_type, amount_of_lessons in spec.items():
            count = 0
            for module in modules_by_type[abbrev]:
                if module['abbrev'] == abbrev and module['type'] == module_type:
                    count += 1
            if count != amount_of_lessons:
                raise Exception('The solution is invalid! Expected %s Lessons in %s of type %s '
                                '(But %s were found)' % (amount_of_lessons, abbrev,
                                                         module_type, count))
        spec['abbrev'] = abbrev
