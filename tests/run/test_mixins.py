from unittest.mock import patch

from clinner.command import command
from clinner.run import HealthCheckMixin
from clinner.run.main import Main


class FooMain(HealthCheckMixin, Main):
    def health_check(self):
        return True


class TestCaseHealthCheckMixin:
    @patch('clinner.run.base.CLI')
    def test_main_add_arguments(self, cli):
        @command
        def foo(*args, **kwargs):
            pass

        args = ['-r', '3', 'foo']
        main = FooMain(args)

        assert main.args.retry == 3

        del command.register['foo']

    @patch('clinner.run.base.CLI')
    def test_main_run(self, cli):
        @command
        def foo(*args, **kwargs):
            return 0

        args = ['-q', 'foo']
        main = FooMain(args)
        result = main.run()

        assert result == 0

        del command.register['foo']

    @patch('clinner.run.base.CLI')
    def test_main_health_check_fails(self, cli):
        @command
        def foo(*args, **kwargs):
            return 0

        args = ['-q', '-r', '1', 'foo']
        main = FooMain(args)
        main.health_check = lambda: False
        result = main.run()

        assert result == 1

        del command.register['foo']

    @patch('clinner.run.base.CLI')
    def test_main_skip_health_check(self, cli):
        @command
        def foo(*args, **kwargs):
            return 0

        args = ['-q', '--skip-check', 'foo']
        main = FooMain(args)
        main.health_check = lambda: False
        result = main.run()

        assert result == 0

        del command.register['foo']

    @patch('clinner.run.base.CLI')
    def test_main_retry_zero(self, cli):
        @command
        def foo(*args, **kwargs):
            return 0

        args = ['-q', '-r', '0', 'foo']
        main = FooMain(args)
        main.health_check = lambda: False
        result = main.run()

        assert result == 0

        del command.register['foo']
