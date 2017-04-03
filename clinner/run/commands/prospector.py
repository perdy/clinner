import shlex

from clinner.command import Type, command

__all__ = ['prospector']


@command(command_type=Type.SHELL,
         parser_opts={'help': 'Run prospector lint'})
def prospector(*args, **kwargs):
    return [shlex.split('prospector')]
