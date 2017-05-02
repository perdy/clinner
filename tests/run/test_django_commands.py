from unittest.case import TestCase
from unittest.mock import MagicMock, call

from clinner.run import DjangoCommand


class FooMain(MagicMock):
    description = 'Foo'


class FooDjangoCommand(DjangoCommand):
    main_class = FooMain


class DjangoCommandTestCase(TestCase):
    def setUp(self):
        self.command = FooDjangoCommand()

    def test_django_command_add_arguments(self):
        parser = MagicMock()
        self.command.add_arguments(parser)

        self.assertEqual(self.command.command._commands_arguments.call_count, 1)

    def test_django_command_handle(self):
        expected_calls = [call(foo='bar')]

        self.command.handle(foo='bar')

        self.assertEqual(self.command.command.run.call_args_list, expected_calls)
