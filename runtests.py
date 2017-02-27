#!/usr/local/env python
# -*- coding: utf-8 -*-
import argparse
import logging
import shlex
import sys

import nose
import prospector.run as prospector

__all__ = ['RunTests', 'main']


class RunTests:
    description = 'Run lint and tests'

    def __init__(self):
        parsed_args = self.parse_arguments()
        self.test_module = parsed_args['test_module']
        self.test_args = shlex.split(' '.join(parsed_args['test_args']))
        self.skip_lint = parsed_args['skip_lint']
        self.skip_tests = parsed_args['skip_tests']
        self.ignore_fail = parsed_args['ignore_fail']

        logging.basicConfig(level=logging.WARNING, format='[%(levelname)s: %(name)s] %(message)s', stream=sys.stderr)
        self.logger = logging.getLogger('runtests')

    def add_arguments(self, parser):
        parser.add_argument('--skip-lint', action='store_true', help='Skip lint')
        parser.add_argument('--skip-tests', action='store_true', help='Skip tests')
        parser.add_argument('--ignore-fail', action='store_true', help='Ignore step fails')
        parser.add_argument('test_module', nargs='*', default=['.'], help='Module to test')
        parser.add_argument('--test_args', action='store', default=[], nargs=argparse.REMAINDER,
                            help='Extra arguments to pass to tests')

    def parse_arguments(self):
        parser = argparse.ArgumentParser(description=self.description)
        self.add_arguments(parser)
        return {k: v for k, v in vars(parser.parse_args()).items()}

    def tests(self):
        argv = ['nosetests'] + self.test_module + self.test_args
        try:
            result = nose.run(argv=argv)
            result = (result + 1) % 2  # Change 0 to 1 and 1 to 0
        except:
            self.logger.exception('Tests failed')
            result = 1

        return result

    def lint(self):
        argv = sys.argv
        sys.argv = []
        try:
            result = prospector.main()
        except:
            self.logger.exception('Lint failed')
            result = 1
        finally:
            sys.argv = argv

        return result

    def _check_exit(self, result):
        print('Return code: {:d}'.format(result))
        if not self.ignore_fail and result:
            sys.exit(result)
        else:
            return result

    def run(self):
        result = 0

        if not self.skip_lint:
            result |= self._check_exit(self.lint())

        if not self.skip_tests:
            result |= self._check_exit(self.tests())

        return result


def main():
    return RunTests().run()


if __name__ == '__main__':
    sys.exit(main())
