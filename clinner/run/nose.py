import sys
from contextlib import contextmanager

import nose as _nose
import prospector.run as prospector

from clinner.command import command
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
    @command(args=((('test_module',), {'nargs': '*', 'default': ['.'], 'help': 'Module to test'}),),
             parser_opts={'help': 'Run unit tests'})
    def tests(*args, **kwargs):
        with clean_argv():
            try:
                sys.argv = []
                argv = ['nosetests'] + kwargs['test_module'] + list(args)
                result = _nose.run(argv=argv)
                result = (result + 1) % 2  # Change 0 to 1 and 1 to 0
            except:
                result = 1

        return result

    @staticmethod
    @command(parser_opts={'help': 'Run lint'})
    def lint(*args, **kwargs):
        with clean_argv():
            try:
                result = prospector.main()
            except:
                result = 1

        return result

    @staticmethod
    @command(args=((('--skip-lint',), {'action': 'store_true', 'help': 'Skip lint'}),
                   (('--skip-tests',), {'action': 'store_true', 'help': 'Skip tests'}),
                   (('--ignore-fail',), {'action': 'store_true', 'help': 'Ignore step failures'}),
                   (('test_module',), {'nargs': '*', 'default': ['.'], 'help': 'Module to test'})),
             parser_opts={'help': 'Run unit tests and lint'})
    def nose(*args, **kwargs):
        result = 0

        if not kwargs['skip_lint']:
            result |= _check_exit(Nose.lint(*args, **kwargs), kwargs['ignore_fail'])

        if not kwargs['skip_tests']:
            result |= _check_exit(Nose.tests(*args, **kwargs), kwargs['ignore_fail'])

        return result
