class WrongCommandError(KeyError):
    pass


class WrongResourceError(KeyError):
    pass


class CommandTypeError(TypeError):
    pass
