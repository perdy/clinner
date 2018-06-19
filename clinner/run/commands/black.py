import shlex

from clinner.command import Type, command

__all__ = ["black"]


@command(command_type=Type.SHELL, parser_opts={"help": "Run black"})
def black(*args, **kwargs):
    """
    Run prospector lint.
    """
    return [shlex.split("black") + list(args)]
