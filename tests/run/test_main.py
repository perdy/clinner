import sys
from unittest.case import TestCase
from unittest.mock import patch

from clinner.builder import Builder
from clinner.command import command, Type
from clinner.run.main import Main


class MainTestCase(TestCase):
    def setUp(self):
        sys.argv = ['test']
        command.register.clear()

    def test_command(self):
        @command
        def foo(*args, **kwargs):
            return 42

        args = ['-q', 'foo']
        main = Main(args)
        expected_target = Builder.build_command('foo')[0][0].func
        with patch('clinner.run.base.Process') as process_mock:
            main.run()

        self.assertEqual(process_mock.call_count, 1)
        self.assertEqual(process_mock.call_args[1]['target'].func, expected_target)

    def test_command_python(self):
        @command(command_type=Type.python)
        def foo(*args, **kwargs):
            return 42

        args = ['-q', 'foo']
        main = Main(args)
        expected_target = Builder.build_command('foo')[0][0].func
        with patch('clinner.run.base.Process') as process_mock:
            main.run()

        self.assertEqual(process_mock.call_count, 1)
        self.assertEqual(process_mock.call_args[1]['target'].func, expected_target)

    def test_command_bash(self):
        @command(command_type=Type.bash)
        def foo(*args, **kwargs):
            return [['foo']]

        args = ['-q', 'foo']
        main = Main(args)
        with patch('clinner.run.base.Popen') as popen_mock:
            popen_mock.return_value.returncode = 0
            main.run()

        self.assertEqual(popen_mock.call_count, 1)
        self.assertEqual(popen_mock.call_args[1]['args'], ['foo'])

    def test_command_multiple_bash(self):
        @command(command_type=Type.bash)
        def foo(*args, **kwargs):
            return [['foo'], ['bar']]

        args = ['-q', 'foo']
        main = Main(args)
        with patch('clinner.run.base.Popen') as popen_mock:
            popen_mock.return_value.returncode = 0
            main.run()

        self.assertEqual(popen_mock.call_count, 2)
        print(popen_mock.call_args_list)
        self.assertEqual(popen_mock.call_args_list[0][1]['args'], ['foo'])
        self.assertEqual(popen_mock.call_args_list[1][1]['args'], ['bar'])

    def tearDown(self):
        pass
