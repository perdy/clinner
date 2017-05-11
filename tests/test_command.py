import sys
from multiprocessing import Queue
from unittest.case import TestCase
from unittest.mock import patch

import pytest

from clinner.command import Type, command
from clinner.exceptions import CommandArgParseError, CommandTypeError, WrongCommandError
from clinner.run.main import Main


class CommandRegisterTestCase(TestCase):
    @pytest.fixture(autouse=True)
    def create_command(self):
        @command
        def foo(*args, **kwargs):
            return 42

        yield

        del command.register['foo']

    def test_command(self):
        self.assertTrue('foo' in command.register)

    def test_get_wrong_command(self):
        with self.assertRaises(WrongCommandError):
            command.register['wrong_command']


class CommandTestCase(TestCase):
    def setUp(self):
        sys.argv = ['test']
        self.cli_patcher = patch('clinner.run.base.CLI')
        self.cli_patcher.start()

    def test_command(self):
        @command
        def foo(*args, **kwargs):
            kwargs['q'].put(42)

        queue = Queue()
        args = ['foo']
        Main(args).run(q=queue)

        self.assertEqual(queue.get(), 42)

    def test_command_python(self):
        @command(command_type=Type.PYTHON)
        def foo(*args, **kwargs):
            kwargs['q'].put(42)

        queue = Queue()
        args = ['foo']
        Main(args).run(q=queue)

        self.assertEqual(queue.get(), 42)

    def test_command_with_args(self):
        @command(command_type=Type.PYTHON,
                 args=((('-b', '--bar'),),))  # args
        def foo(*args, **kwargs):
            kwargs['q'].put(kwargs['bar'])

        queue = Queue()
        args = ['foo']
        Main(args).run(bar='foobar', q=queue)

        self.assertEqual(queue.get(), 'foobar')

    def test_command_with_args_and_opts(self):
        @command(command_type=Type.PYTHON,
                 args=((('-b', '--bar'), {'type': int, 'help': 'bar argument'}),))  # args and opts
        def foo(*args, **kwargs):
            kwargs['q'].put(kwargs['bar'])

        queue = Queue()
        args = ['foo']
        Main(args).run(bar=3, q=queue)

        self.assertEqual(queue.get(), 3)

    def test_command_with_callable_args(self):
        def add_arguments(parser):
            parser.add_argument('-b', '--bar', type=int, help='bar argument')

        @command(args=add_arguments)
        def foo(*args, **kwargs):
            kwargs['q'].put(kwargs['bar'])

        queue = Queue()
        args = ['foo']
        Main(args).run(bar=3, q=queue)

        self.assertEqual(queue.get(), 3)

    def test_command_with_wrong_args_number(self):
        @command(command_type=Type.PYTHON,
                 args=(((1, 2, 3),)))  # wrong args number
        def foo(*args, **kwargs):
            kwargs['q'].put(kwargs['bar'])

        args = ['foo']
        self.assertRaises(CommandArgParseError, Main, args)

    def test_command_with_unknown_args(self):
        @command  # args
        def foo(*args, **kwargs):
            kwargs['q'].put(args[0])

        queue = Queue()
        args = ['foo']
        Main(args).run('foobar', q=queue)

        self.assertEqual(queue.get(), 'foobar')

    def test_command_shell(self):
        @command(command_type=Type.SHELL)
        def foo(*args, **kwargs):
            return [['foo']]

        args = ['foo']
        main = Main(args)
        with patch('clinner.run.base.Popen') as popen_mock:
            popen_mock.return_value.returncode = 0
            main.run()

        self.assertEqual(popen_mock.call_count, 1)
        self.assertEqual(popen_mock.call_args[1]['args'], ['foo'])

    def test_command_multiple_shell(self):
        @command(command_type=Type.SHELL)
        def foo(*args, **kwargs):
            return [['foo'], ['bar']]

        args = ['foo']
        main = Main(args)
        with patch('clinner.run.base.Popen') as popen_mock:
            popen_mock.return_value.returncode = 0
            main.run()

        self.assertEqual(popen_mock.call_count, 2)
        self.assertEqual(popen_mock.call_args_list[0][1]['args'], ['foo'])
        self.assertEqual(popen_mock.call_args_list[1][1]['args'], ['bar'])

    def test_command_multiple_shell_failing(self):
        @command(command_type=Type.SHELL)
        def foo(*args, **kwargs):
            return [['foo'], ['bar']]

        args = ['foo']
        main = Main(args)
        with patch('clinner.run.base.Popen') as popen_mock:
            popen_mock.return_value.returncode = 1
            main.run()

        self.assertEqual(popen_mock.call_count, 1)
        self.assertEqual(popen_mock.call_args_list[0][1]['args'], ['foo'])

    def test_command_wrong_type(self):
        @command(command_type='foo')
        def foo(*args, **kwargs):
            pass

        args = ['foo']
        self.assertRaises(CommandTypeError, Main(args).run, args)

    def tearDown(self):
        self.cli_patcher.stop()
        del command.register['foo']
