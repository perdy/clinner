from unittest.case import TestCase
from unittest.mock import patch

from clinner.command import command
from clinner.run import HealthCheckMixin
from clinner.run.main import Main


class FooMain(HealthCheckMixin, Main):
    def health_check(self):
        return True


class HealthCheckMixinTestCase(TestCase):
    def setUp(self):
        self.cli_patcher = patch('clinner.run.base.CLI')
        self.cli_patcher.start()

    def test_main_add_arguments(self):
        @command
        def foo(*args, **kwargs):
            pass

        args = ['-r', '3', 'foo']
        main = FooMain(args)

        self.assertEqual(main.args.retry, 3)

    def test_main_run(self):
        @command
        def foo(*args, **kwargs):
            return 0

        args = ['-q', 'foo']
        main = FooMain(args)
        result = main.run()

        self.assertEqual(result, 0)

    def test_main_health_check_fails(self):
        @command
        def foo(*args, **kwargs):
            return 0

        args = ['-q', '-r', '1', 'foo']
        main = FooMain(args)
        main.health_check = lambda: False
        result = main.run()

        self.assertEqual(result, 1)

    def test_main_skip_health_check(self):
        @command
        def foo(*args, **kwargs):
            return 0

        args = ['-q', '--skip-check', 'foo']
        main = FooMain(args)
        main.health_check = lambda: False
        result = main.run()

        self.assertEqual(result, 0)

    def test_main_retry_zero(self):
        @command
        def foo(*args, **kwargs):
            return 0

        args = ['-q', '-r', '0', 'foo']
        main = FooMain(args)
        main.health_check = lambda: False
        result = main.run()

        self.assertEqual(result, 0)

    def tearDown(self):
        self.cli_patcher.stop()
        del command.register['foo']
