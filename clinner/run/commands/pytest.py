import shlex

from clinner.command import Type, command

__all__ = ['pytest']


@command(command_type=Type.SHELL,
         args=((('test_module',), {'nargs': '*', 'default': ['.'], 'help': 'Module to test'}),),
         parser_opts={'help': 'Run unit tests'})
def pytest(*args, **kwargs):
    """
    Run unit tests using pytest.
    """
    coverage_erase = shlex.split('coverage erase')

    tests = shlex.split('pytest')
    tests += args

    return [coverage_erase, tests]
