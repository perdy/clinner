import shlex

from clinner.command import Type, command

__all__ = ["flake8"]


@command(command_type=Type.SHELL, parser_opts={"help": "Run flake8"})
def flake8(*args, **kwargs):
    """
    Run prospector lint.
    """
    return [shlex.split("flake8") + list(args)]
