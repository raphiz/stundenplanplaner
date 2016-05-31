
class DatasourceException(Exception):
    pass


class AuthenticationException(DatasourceException):
    pass


class ScraperException(DatasourceException):
    pass
