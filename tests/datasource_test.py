from planner import AdUnisHSR, AuthenticationException, utils
import pytest
import re
from configparser import ParsingError
from vcr import VCR
from datetime import time

vcr = VCR(cassette_library_dir='fixtures/')


@vcr.use_cassette
def test_signin_invalid_credentials():
    source = AdUnisHSR()

    with pytest.raises(AuthenticationException) as exceptionInfo:
        source.signin('user', 'password')

    assert str(exceptionInfo.value) == "Authentication has failed (Status code was 401)!"


@vcr.use_cassette
def test_in_hsr_network():
    source = AdUnisHSR()
    assert source._in_HSR_network()


@vcr.use_cassette
def test_signin_valid_credentials():
    source = AdUnisHSR()
    username, password = utils.parse_user_credentials('auth.cfg')
    response = source.signin(username, password)
    assert len(response.text) > 100


@vcr.use_cassette
def test_all_modules_ids_not_signed_in():
    source = AdUnisHSR()

    with pytest.raises(AuthenticationException) as exceptionInfo:
        source.all_modules_ids()

    assert str(exceptionInfo.value) == "You must log in before you can query!"


@vcr.use_cassette
def test_all_modules_ids_signed_in_happy_path():
    source = AdUnisHSR()

    username, password = utils.parse_user_credentials('auth.cfg')
    response = source.signin(username, password)
    modules = source.all_modules_ids()
    assert len(modules) > 20
    assert modules['InfSys'] == '51677'


@vcr.use_cassette
def test_lectures_times_happy_path():
    source = AdUnisHSR()

    username, password = utils.parse_user_credentials('auth.cfg')
    response = source.signin(username, password)

    if 'CN1' in source.all_modules_ids():
        # Herbstsemester
        lectures_times = source.lectures_times(['CN1'])
        raise Exception("NOT TESTET YET! PLEASE IMPLEMENT ME!")
    else:
        # Fruehlungssemester
        lectures_times = source.lectures_times(['CN2'])['CN2']
        # Uebungen
        uebungen = [lectures_times for lt in lectures_times if lt['type'] == 'u']
        assert len(uebungen) >= 2 and len(uebungen) < len(lectures_times)
        # Praktikas
        praktikas = [lectures_times for lt in lectures_times if lt['type'] == 'u']
        assert len(praktikas) >= 4 and len(uebungen) < len(lectures_times)
        # Vorlesungen
        vorlesungen = [lectures_times for lt in lectures_times if lt['type'] == 'v']
        assert len(vorlesungen) >= 2 and len(uebungen) < len(lectures_times)

    # TODO: Test for more modules
    begin_first_lesson = time(7, 5)
    begin_last_lesson = time(20, 5)
    for lesson in lectures_times:
        assert re.match('^CN(1|2)(Prak)?-(u|v|p)[0-9][0-9]?$', lesson['name']) is not None
        assert re.match('^CN(1|2)(Prak)?$', lesson['abbrev']) is not None
        assert begin_first_lesson <= lesson['start_time'] <= begin_last_lesson
        assert re.match('^[A-Z]{3}( [A-Z]{3})*$', lesson['teacher']) is not None
        assert lesson['day'] in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        assert lesson['class'] is not None
        assert lesson['team'] is None or re.match('^[0-9]$', lesson['class'])
        assert re.match('^[1-9]\.[0-9]*[a-z]?$', lesson['room']) is not None
        # TODO: weeks
