from planner import AdUnisHSR
from planner import utils

from datetime import datetime

from isoweek import Week

import vcr

with vcr.use_cassette('fixtures/demo_exort', record_mode='new_episodes'):
    source = AdUnisHSR()
    username, password = utils.parse_user_credentials('auth.cfg')
    response = source.signin(username, password)

    my_id = '5011205'

    my_timetable = source.lessons_for_student(AdUnisHSR.NEXT_SEMESTER, my_id)

    semester_start = datetime(2016, 9, 19)
    semester_end = datetime(2016, 12, 23)

    utils.export_to_ical('modules.ics', my_timetable, start=semester_start, end=semester_end)
    # Equivalent to:
    # utils.export_to_ical('modules.ics', my_timetable, year=2016, weeks=range(38, 52))
