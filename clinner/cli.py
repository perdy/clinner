import logging
import typing
from collections import OrderedDict

from clinner.command import Type

try:
    import colorlog

    _colorlog = True
except ImportError:  # pragma: no cover
    _colorlog = False

__all__ = ["CLI"]


class CLI:
    """
    command Line Interface helpers, such as predefined styles for different type of messages, headers, etc.
    """

    SEP = "-" * 70

    def __init__(self, level=logging.INFO):
        if _colorlog:
            self.handler = colorlog.StreamHandler()
            self.handler.setFormatter(
                colorlog.ColoredFormatter(
                    "%(log_color)s%(message)s",
                    datefmt=None,
                    reset=True,
                    log_colors={
                        "DEBUG": "cyan",
                        "INFO": "green",
                        "WARNING": "yellow",
                        "ERROR": "red",
                        "CRITICAL": "red,bg_white",
                    },
                    style="%",
                )
            )
        else:
            #  Default to basic logging
            self.handler = logging.StreamHandler()

        self.logger = logging.getLogger("cli")
        self.logger.addHandler(self.handler)
        self.logger.setLevel(level)
        self.logger.propagate = False

    def disable(self):
        self.logger.removeHandler(self.handler)

    def enable(self):
        self.logger.addHandler(self.handler)

    def set_level(self, level):
        self.logger.setLevel(level)

    def print_return(self, code: typing.Optional[int]):
        if code is None:
            code = 0

        level = logging.DEBUG if code == 0 else logging.ERROR
        self.logger.log(level, "Return code: %d", code)

    def print_header(self, **kwargs):
        command = kwargs.pop("command")
        header = "{0}\n{1}\n{0}".format(self.SEP, command)
        self.logger.info(header)

        fields = OrderedDict(sorted(kwargs.items(), key=lambda x: x[0]))
        fmt = "{:<%d}: {}" % (max([len(x) for x in fields.keys()]),)
        command_args = "---------\nArguments\n---------\n" + "\n".join([fmt.format(k, v) for k, v in fields.items()])
        self.logger.debug(command_args)

    def print_commands_list(self, command, commands_type: Type):
        if commands_type == Type.PYTHON:
            cmds = " - [{}] {}.{}".format(commands_type.value, str(command.__module__), str(command.__qualname__))
        else:
            cmds = "\n".join([" - [{}] {}".format(commands_type.value, " ".join(c)) for c in command])

        msg = "--------\nCommands\n--------\n" + cmds
        self.logger.debug(msg)
