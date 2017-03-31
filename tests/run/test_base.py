from unittest.case import TestCase
from unittest.mock import patch

from clinner.command import command
from clinner.run.main import Main


class FooMain(Main):
    @staticmethod
    @command
    def foo(*args, **kwargs):
        pass

    def add_arguments(self, parser: 'argparse.ArgumentParser'):
        parser.add_argument('-f', '--foo', type=int, help='')

    def inject_foo(self):
        self.foo = True


class BaseMainTestCase(TestCase):
    def setUp(self):
        self.cli_patcher = patch('clinner.run.base.CLI')
        self.cli_patcher.start()

    def test_main_inject(self):
        args = ['foo']
        main = FooMain(args)

        self.assertTrue(getattr(main, 'foo', False))

    def test_main_add_arguments(self):
        args = ['-f', '3', 'foo']
        main = FooMain(args)

        self.assertEqual(main.args.foo, 3)

    def test_main_quiet(self):
        args = ['-q', 'foo']
        main = FooMain(args)

        self.assertEqual(main.cli.disable.call_count, 1)

    def tearDown(self):
        self.cli_patcher.stop()

    @classmethod
    def tearDownClass(cls):
        super(BaseMainTestCase, cls).tearDownClass()
        command.register.clear()
