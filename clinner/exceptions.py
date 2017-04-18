class WrongCommandError(KeyError):
    pass


class WrongResourceError(KeyError):
    pass


class CommandTypeError(TypeError):
    pass


class CommandArgParseError(ValueError):
    pass


class ImproperlyConfigured(Exception):
    pass
