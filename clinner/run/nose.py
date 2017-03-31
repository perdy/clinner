import shlex
import sys
from contextlib import contextmanager

from clinner.command import Type, command
from clinner.run import Main

__all__ = ['Nose']


def _check_exit(result, ignore_fail):
    if not ignore_fail and result:
        sys.exit(result)
    else:
        return result


@contextmanager
def clean_argv():
    old_argv = sys.argv
    sys.argv = []
    yield
    sys.argv = old_argv


class Nose(Main):
    @staticmethod
    @command(command_type=Type.bash,
             args=((('test_module',), {'nargs': '*', 'default': ['.'], 'help': 'Module to test'}),),
             parser_opts={'help': 'Run unit tests'})
    def tests(*args, **kwargs):
        coverage_erase = shlex.split('coverage erase')

        tests = shlex.split('nosetests')
        tests += args

        return [coverage_erase, tests]

    @staticmethod
    @command(command_type=Type.bash,
             parser_opts={'help': 'Run lint'})
    def lint(*args, **kwargs):
        return [shlex.split('prospector')]
