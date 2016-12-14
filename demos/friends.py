from planner import AdUnisHSR
from planner import utils

source = AdUnisHSR()
username, password = utils.parse_user_credentials('auth.cfg')
response = source.signin(username, password)

friends = [
    ('5012019', 'Jonas'),
    ('540793', 'Robin'),
    ('5011745', 'Nikola'),
    ('5011941', 'Fabian'),
    ('5011287', 'Marcel')
    # [...]
]

my_id = '5011205'

my_timetable = sorted(list(set((l['name'] for l in source.lessons_for_student(AdUnisHSR.NEXT_SEMESTER, my_id)))))
friends_timetables = {}

for friend_id, name in friends:
    friends_timetables[name] = set((l['name'] for l in source.lessons_for_student(AdUnisHSR.NEXT_SEMESTER, friend_id)))

for module in my_timetable:
    print(module + ':')
    for name, friend_timetable in friends_timetables.items():
        if module in friend_timetable:
            print(' ' + name)
    print('')
