
class TimeTableException(Exception):
    pass


class DatasourceException(TimeTableException):
    pass


class AuthenticationException(DatasourceException):
    pass


class ScraperException(DatasourceException):
    pass
