from planner import AdUnisHSR, AuthenticationException, utils
import pytest
from configparser import ParsingError
import vcr


def test_signin_invalid_credentials():
    source = AdUnisHSR()

    with pytest.raises(AuthenticationException) as exceptionInfo:
        source.signin('user', 'password')

    assert str(exceptionInfo.value) == "Authentication has failed (Status code was 401)!"


def test_signin_valid_credentials():
    with vcr.use_cassette('fixtures/test_signin_valid_credentials.yaml'):
        source = AdUnisHSR()
        username, password = utils.parse_user_credentials('auth.cfg')
        response = source.signin(username, password)
        assert len(response.text) > 100


def test_all_modules_not_signed_in():
    source = AdUnisHSR()

    with pytest.raises(AuthenticationException) as exceptionInfo:
        source.all_modules()

    assert str(exceptionInfo.value) == "You must log in before you can query!"


def test_all_modules_signed_in_happy_path():
    source = AdUnisHSR()

    with vcr.use_cassette('fixtures/test_all_modules_signed_in_happy_path.yaml'):
        username, password = utils.parse_user_credentials('auth.cfg')
        response = source.signin(username, password)
        modules = source.all_modules()
        assert len(modules) > 20
        assert modules['InfSys'] == '51677'
