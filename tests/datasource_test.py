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

    assert str(exceptionInfo.value)[:27] == "Authentication has failed ("


@vcr.use_cassette
def test_signin_valid_credentials():
    source = AdUnisHSR()
    username, password = utils.parse_user_credentials('auth.cfg')
    source.signin(username, password)
    # No exception means OK!
