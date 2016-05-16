from datetime import datetime, date, timedelta


class Restriction:
    is_filter = False
    is_constraint = False


class OnlyTeacher(Restriction):
    is_filter = True

    #  TODO: replace abbrev with module id
    def __init__(self, module_name, teacher_id):
        self.module_name = module_name
        self.teacher_id = teacher_id

    def filter(self, lesson):
        if lesson['abbrev'] == self.module_name and lesson['teacher'] != self.teacher_id:
            return False
        return True

    def __repr__(self):
        return "Only Teacher %s in %s (OnlyTeacher)" % (self.teacher_id, self.module_name)


class MinChance(Restriction):
    is_filter = True

    def __init__(self, chance, accept_empty=True):
        self.chance = chance
        self.accept_empty = accept_empty

    def filter(self, lesson):
        if 'chance' not in lesson.keys():
            return self.accept_empty
        if (lesson['chance']*100) < self.chance:
            return False
        return True

    def __repr__(self):
        if self.accept_empty:
            return "Only Modules with a chance > %s or no chance defined (MinChance)" % self.chance
        return "Only Modules with a chance > %s (MinChance)" % self.chance


class InTimeRange(Restriction):
    is_filter = True

    def __init__(self, start_time, end_time):
        self.start_time = start_time
        self.end_datetime = datetime.combine(date.today(), end_time)

    def filter(self, lesson):
        end_by = datetime.combine(date.today(), lesson['start_time']) + timedelta(minutes=45)
        if lesson['start_time'] < self.start_time or end_by > self.end_datetime:
            return False
        return True

    def __repr__(self):
        return "Only Lessons between %s and %s (InTimeRange)" % (self.start_time,
                                                                 self.end_datetime.time())


class FreeTime(Restriction):

    is_constraint = True

    _DAYS_OF_THE_WEEK = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    def __init__(self, how_often, days, min_start, min_stop):
        self.how_often = how_often
        self.days = days
        self.min_start = min_start
        self.min_stop = min_stop

    def _time_in_range(self, start, end, x):
        """Return true if x is in the range [start, end]"""
        return x > start and x < end

    def constraint(self, *args):
        # # How often this kind free time shall take place
        # how_often = 1
        #
        # # Which days (here Mon-Fri)
        # days = range(5)
        #
        # # The time in which no lectures shall take place
        # min_start = time(12)
        # min_stop = time(23)
        slots = [True for x in range(7)]
        for module in args:
            for lesson in module:
                if self._time_in_range(self.min_start, self.min_stop, lesson['start_time']):
                    slots[self._DAYS_OF_THE_WEEK.index(lesson['day'])] = False

        if len([x for x in slots[self.days[0]:self.days[-1]+1] if x]) < self.how_often:

            return False
        return True
