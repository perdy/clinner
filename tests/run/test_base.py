import argparse
from unittest.case import TestCase
from unittest.mock import patch

from multiprocessing import Queue

import pytest

from clinner.command import command, Type
from clinner.run.main import Main


class BaseMainTestCase(TestCase):
    @pytest.fixture(autouse=True)
    def define_main(self):
        class FooMain(Main):
            @staticmethod
            @command
            def foo(*args, **kwargs):
                return 42

            @staticmethod
            @command(command_type=Type.SHELL)
            def bar(*args, **kwargs):
                return [[]]

            def add_arguments(self, parser: 'argparse.ArgumentParser'):
                parser.add_argument('-f', '--foo', type=int, help='')

            def inject_foo(self):
                self.foo = True

        self.main_cls = FooMain

    def setUp(self):
        self.cli_patcher = patch('clinner.run.base.CLI')
        self.cli_patcher.start()

    def test_main_inject(self):
        args = ['foo']
        main = self.main_cls(args)

        self.assertTrue(getattr(main, 'foo', False))

    def test_main_add_arguments(self):
        args = ['-f', '3', 'foo']
        main = self.main_cls(args)

        self.assertEqual(main.args.foo, 3)

    def test_main_quiet(self):
        args = ['-q', 'foo']
        main = self.main_cls(args)

        self.assertEqual(main.cli.disable.call_count, 1)

    def test_dry_run_python(self):
        args = ['--dry-run', 'foo']
        main = self.main_cls(args)

        result = main.run()

        self.assertEqual(result, 0)

    def test_dry_run_shell(self):
        args = ['--dry-run', 'bar']
        main = self.main_cls(args)

        with patch('clinner.run.base.Popen') as popen_mock:
            main.run()

        self.assertEqual(popen_mock.call_count, 0)

    def test_explicit_commands(self):
        class BarMain(Main):
            commands = ('tests.run.utils_base.foobar',)

        args = ['foobar']
        main = BarMain(args)
        queue = Queue()
        main.run(q=queue)

        self.assertEqual(queue.get(), 42)

    def test_explicit_command_wrong(self):
        with self.assertRaises(ImportError):
            class BarMain(Main):
                commands = ('tests.run.utils_base.wrong_command',)

    def test_replace_explicit_commands(self):
        class BarMain(Main):
            commands = ('tests.run.utils_base.foobar',)

            @staticmethod
            @command
            def foobar(*args, **kwargs):
                kwargs['q'].put(1)

        args = ['foobar']
        main = BarMain(args)
        queue = Queue()
        main.run(q=queue)

        self.assertEqual(queue.get(), 1)

    def test_parse_args_with_parser(self):
        parser = argparse.ArgumentParser()

        main = self.main_cls(parse_args=False)
        args, _ = main.parse_arguments(args=['-f', '1', 'foo'], parser=parser)

        self.assertEqual(args.foo, 1)

    def tearDown(self):
        self.cli_patcher.stop()
