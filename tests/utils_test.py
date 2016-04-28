from planner import utils
import pytest
from configparser import ParsingError


def test_parse_user_credentials_with_invalid_format():
    with pytest.raises(ParsingError):
        utils.parse_user_credentials('tests/files/broken.cfg')


def test_parse_user_credentials_with_missing_file():
    with pytest.raises(AssertionError):
        utils.parse_user_credentials('tests/files/not_exist.cfg')


def test_parse_user_credentials_happy_path():
    (username, password) = utils.parse_user_credentials('tests/files/valid.cfg')
    assert username == 'mmuster'
    assert password == 'pass'
