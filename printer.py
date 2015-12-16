from tabulate import tabulate

DAYS_OF_THE_WEEK = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']


def verify(timetable):

    def lessons_for_type(abbrev, ltype):
        return filter(lambda l: l['abbrev'] == abbrev and l['type'] == ltype, timetable)

    assert 2 == len(lessons_for_type('AD1', 'v'))
    assert 2 == len(lessons_for_type('AD1', 'u'))

    assert 3 == len(lessons_for_type('An2I', 'v'))
    assert 1 == len(lessons_for_type('An2I', 'u'))

    assert 3 == len(lessons_for_type('AutoSpr', 'v'))
    assert 1 == len(lessons_for_type('AutoSpr', 'u'))

    assert 2 == len(lessons_for_type('ExEv', 'v'))
    assert 2 == len(lessons_for_type('ExEv', 'u'))

    assert 2 == len(lessons_for_type('InfSi1', 'v'))
    assert 2 == len(lessons_for_type('InfSi1', 'u'))

    # assert 2 == len(lessons_for_type('TKI', 'v'))
    # assert 2 == len(lessons_for_type('TKI', 'u'))

    assert 2 == len(lessons_for_type('RKI', 'v'))
    assert 2 == len(lessons_for_type('RKI', 'u'))

    assert 2 == len(lessons_for_type('WED1', 'v'))
    assert 2 == len(lessons_for_type('WED1', 'u'))

    # assert 32 + 7 == len(timetable)
    assert 32 == len(timetable)


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
