import argparse
import logging
from multiprocessing import Queue
from unittest.mock import call, patch

import pytest

from clinner.command import Type, command
from clinner.run.main import Main


class TestCaseBaseMain:
    @pytest.fixture
    def main_cls(self):
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

        return FooMain

    @patch('clinner.run.base.CLI')
    def test_main_inject(self, cli, main_cls):
        args = ['foo']
        main = main_cls(args)

        assert getattr(main, 'foo', False)

    @patch('clinner.run.base.CLI')
    def test_main_add_arguments(self, cli, main_cls):
        args = ['-f', '3', 'foo']
        main = main_cls(args)

        assert main.args.foo == 3

    @patch('clinner.run.base.CLI')
    def test_main_quiet(self, cli, main_cls):
        args = ['-q', 'foo']
        main = main_cls(args)

        assert main.cli.disable.call_count == 1

    @patch('clinner.run.base.CLI')
    def test_main_verbose_1(self, cli, main_cls):
        args = ['-v', 'foo']
        main = main_cls(args)

        assert main.cli.set_level.call_args_list == [call(logging.INFO)]

    @patch('clinner.run.base.CLI')
    def test_main_verbose_2(self, cli, main_cls):
        args = ['-vv', 'foo']
        main = main_cls(args)

        assert main.cli.set_level.call_args_list == [call(logging.DEBUG)]

    @patch('clinner.run.base.CLI')
    def test_main_verbose_no_explicit(self, cli, main_cls):
        args = ['foo']
        main = main_cls(args)

        assert main.cli.set_level.call_args_list == [call(logging.INFO)]

    @patch('clinner.run.base.CLI')
    def test_dry_run_python(self, cli, main_cls):
        args = ['--dry-run', 'foo']
        main = main_cls(args)

        result = main.run()

        assert result == 0

    @patch('clinner.run.base.CLI')
    def test_dry_run_shell(self, cli, main_cls):
        args = ['--dry-run', 'bar']
        main = main_cls(args)

        with patch('clinner.run.base.Popen') as popen_mock:
            main.run()

        assert popen_mock.call_count == 0

    @patch('clinner.run.base.CLI')
    def test_explicit_local_command(self, cli, main_cls):
        @command
        def foo_command(*args, **kwargs):
            kwargs['q'].put(42)

        class BarMain(Main):
            commands = ('foo_command',)

        args = ['foo_command']
        main = BarMain(args)
        queue = Queue()
        main.run(q=queue)

        assert queue.get() == 42
        assert 'foo_command' in main._commands
        assert len(main._commands) == 1

    @patch('clinner.run.base.CLI')
    def test_explicit_commands(self, cli, main_cls):
        class BarMain(Main):
            commands = ('tests.run.utils_base.foobar',)

        args = ['foobar']
        main = BarMain(args)
        queue = Queue()
        main.run(q=queue)

        assert queue.get() == 42
        assert 'foobar' in main._commands
        assert len(main._commands) == 1

    @patch('clinner.run.base.CLI')
    def test_explicit_command_wrong(self, cli, main_cls):
        with pytest.raises(ImportError):
            class BarMain(Main):
                commands = ('tests.run.utils_base.wrong_command',)

    @patch('clinner.run.base.CLI')
    def test_replace_explicit_commands(self, cli, main_cls):
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

        assert queue.get() == 1

    @patch('clinner.run.base.CLI')
    def test_parse_args_with_parser(self, cli, main_cls):
        parser = argparse.ArgumentParser()

        main = main_cls(parse_args=False)
        args, _ = main.parse_arguments(args=['-f', '1', 'foo'], parser=parser)

        assert args.foo == 1
