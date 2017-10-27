import shlex

from clinner.command import Type, command

__all__ = ['nose']


@command(command_type=Type.SHELL,
         args=((('test_module',), {'nargs': '*', 'default': ['.'], 'help': 'Module to test'}),),
         parser_opts={'help': 'Run unit tests'})
def nose(*args, **kwargs):
    """
    Run unit tests using Nose.
    """
    coverage_erase = shlex.split('coverage erase')

    tests = shlex.split('nosetests')
    tests += args

    return [coverage_erase, tests]
