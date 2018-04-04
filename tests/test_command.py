from multiprocessing import Queue
from unittest.mock import patch

import pytest

from clinner.command import Type, command
from clinner.exceptions import CommandArgParseError, CommandTypeError, WrongCommandError
from clinner.run.main import Main


class TestCaseCommandRegister:
    @pytest.fixture(autouse=True)
    def create_command(self):
        @command
        def foo(*args, **kwargs):
            return 42

        yield

        del command.register['foo']

    def test_command(self):
        assert 'foo' in command.register

    def test_get_wrong_command(self):
        with pytest.raises(WrongCommandError):
            command.register['wrong_command']


class TestCaseCommand:
    @patch('clinner.run.base.CLI')
    def test_command(self, cli):
        @command
        def foo(*args, **kwargs):
            kwargs['q'].put(42)

        queue = Queue()
        args = ['foo']
        Main(args).run(q=queue)

        assert queue.get() == 42

        del command.register['foo']

    @patch('clinner.run.base.CLI')
    def test_command_python(self, cli):
        @command(command_type=Type.PYTHON)
        def foo(*args, **kwargs):
            kwargs['q'].put(42)

        queue = Queue()
        args = ['foo']
        Main(args).run(q=queue)

        assert queue.get() == 42

        del command.register['foo']

    @patch('clinner.run.base.CLI')
    def test_command_with_args(self, cli):
        @command(command_type=Type.PYTHON,
                 args=((('-b', '--bar'),),))  # args
        def foo(*args, **kwargs):
            kwargs['q'].put(kwargs['bar'])

        queue = Queue()
        args = ['foo']
        Main(args).run(bar='foobar', q=queue)

        assert queue.get() == 'foobar'

        del command.register['foo']

    @patch('clinner.run.base.CLI')
    def test_command_with_args_and_opts(self, cli):
        @command(command_type=Type.PYTHON,
                 args=((('-b', '--bar'), {'type': int, 'help': 'bar argument'}),))  # args and opts
        def foo(*args, **kwargs):
            kwargs['q'].put(kwargs['bar'])

        queue = Queue()
        args = ['foo']
        Main(args).run(bar=3, q=queue)

        assert queue.get() == 3

        del command.register['foo']

    @patch('clinner.run.base.CLI')
    def test_command_with_callable_args(self, cli):
        def add_arguments(parser):
            parser.add_argument('-b', '--bar', type=int, help='bar argument')

        @command(args=add_arguments)
        def foo(*args, **kwargs):
            kwargs['q'].put(kwargs['bar'])

        queue = Queue()
        args = ['foo']
        Main(args).run(bar=3, q=queue)

        assert queue.get() == 3

        del command.register['foo']

    @patch('clinner.run.base.CLI')
    def test_command_with_wrong_args_number(self, cli):
        @command(command_type=Type.PYTHON,
                 args=(((1, 2, 3),)))  # wrong args number
        def foo(*args, **kwargs):
            kwargs['q'].put(kwargs['bar'])

        args = ['foo']
        with pytest.raises(CommandArgParseError):
            Main(args)

        del command.register['foo']

    @patch('clinner.run.base.CLI')
    def test_command_with_unknown_args(self, cli):
        @command  # args
        def foo(*args, **kwargs):
            kwargs['q'].put(args[0])

        queue = Queue()
        args = ['foo']
        Main(args).run('foobar', q=queue)

        assert queue.get() == 'foobar'

        del command.register['foo']

    @patch('clinner.run.base.CLI')
    def test_command_shell(self, cli):
        @command(command_type=Type.SHELL)
        def foo(*args, **kwargs):
            return [['foo']]

        args = ['foo']
        main = Main(args)
        with patch('clinner.run.base.Popen') as popen_mock:
            popen_mock.return_value.returncode = 0
            main.run()

        assert popen_mock.call_count == 1
        assert popen_mock.call_args[1]['args'] == ['foo']

        del command.register['foo']

    @patch('clinner.run.base.CLI')
    def test_command_multiple_shell(self, cli):
        @command(command_type=Type.SHELL)
        def foo(*args, **kwargs):
            return [['foo'], ['bar']]

        args = ['foo']
        main = Main(args)
        with patch('clinner.run.base.Popen') as popen_mock:
            popen_mock.return_value.returncode = 0
            main.run()

        assert popen_mock.call_count == 2
        assert popen_mock.call_args_list[0][1]['args'] == ['foo']
        assert popen_mock.call_args_list[1][1]['args'] == ['bar']

        del command.register['foo']

    @patch('clinner.run.base.CLI')
    def test_command_multiple_shell_failing(self, cli):
        @command(command_type=Type.SHELL)
        def foo(*args, **kwargs):
            return [['foo'], ['bar']]

        args = ['foo']
        main = Main(args)
        with patch('clinner.run.base.Popen') as popen_mock:
            popen_mock.return_value.returncode = 1
            main.run()

        assert popen_mock.call_count == 1
        assert popen_mock.call_args_list[0][1]['args'] == ['foo']

        del command.register['foo']

    @patch('clinner.run.base.CLI')
    def test_command_wrong_type(self, cli):
        @command(command_type='foo')
        def foo(*args, **kwargs):
            pass

        args = ['foo']
        with pytest.raises(CommandTypeError):
            Main(args).run(args)

        del command.register['foo']
