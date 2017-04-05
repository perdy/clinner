import shlex

from clinner.command import Type, command

__all__ = ['tox']


@command(command_type=Type.SHELL,
         parser_opts={'help': 'Run tox'})
def tox(*args, **kwargs):
    """
    Run tests using tox.
    """
    return [shlex.split('tox') + list(args)]
