from unittest.mock import MagicMock, call

import pytest

from clinner.run import DjangoCommand


class FooMain(MagicMock):
    description = 'Foo'


class FooDjangoCommand(DjangoCommand):
    main_class = FooMain


class TestCaseDjangoCommand:
    @pytest.fixture
    def command(self):
        return FooDjangoCommand()

    def test_django_command_add_arguments(self, command):
        parser = MagicMock()
        command.add_arguments(parser)

        assert command.command._commands_arguments.call_count == 1

    def test_django_command_handle(self, command):
        expected_calls = [call(foo='bar')]

        command.handle(foo='bar')

        assert command.command.run.call_args_list == expected_calls
