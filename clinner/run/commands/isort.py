import shlex

from clinner.command import Type, command

__all__ = ["isort"]


@command(command_type=Type.SHELL, parser_opts={"help": "Run isort"})
def isort(*args, **kwargs):
    """
    Run prospector lint.
    """
    return [shlex.split("isort") + list(args)]
