from datetime import datetime, date, timedelta

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


def _time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    return x > start and x < end


_DAYS_OF_THE_WEEK = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']


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
                if _time_in_range(min_start, min_stop, lesson['start_time']):
                    slots[_DAYS_OF_THE_WEEK.index(lesson['day'])] = False

        if len([x for x in slots[days[0]:days[-1]+1] if x]) < how_often:

            return False
        return True
    return criteria
