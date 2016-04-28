from configparser import ConfigParser
import os


def parse_user_credentials(path):
    """
        Reads the username and password value from the cfg-file of
        the give path and returns it as a tuple
        (username, password). Raises AssertionError if the file or the
        configurations could not be found.
    """
    config = ConfigParser()
    assert os.path.exists(path), "Missing configurationfile 'auth.cfg'"
    config.read(path)

    assert 'authentication' in config, \
        "Missing authentication section in configuration!"
    assert 'username' in config['authentication'], \
        "Missing username in configuration!"
    assert 'password' in config['authentication'], \
        "Missing username in configuration!"

    return (config['authentication']['username'],
            config['authentication']['password'])
