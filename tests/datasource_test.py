from planner import AdUnisHSR, AuthenticationException, utils
import pytest
from configparser import ParsingError
from vcr import VCR

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
    lectures_times = source.lectures_times(['AD1', 'InfSi1'])
    print(lectures_times)
    # TODO: verify!
