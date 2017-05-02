import logging
from unittest.case import TestCase
from unittest.mock import MagicMock, call, patch

from clinner.cli import CLI


class CLITestCase(TestCase):
    def setUp(self):
        self.cli = CLI()
        self.cli.logger = MagicMock()

    def test_init_with_colorlog(self):
        with patch('clinner.cli._colorlog', True), patch('colorlog.StreamHandler') as handler_mock:
            CLI()

            self.assertTrue(handler_mock.call_count, 1)
            self.assertTrue(handler_mock.return_value.setFormatter.call_count, 1)

    def test_init_without_colorlog(self):
        with patch('clinner.cli._colorlog', False), patch('clinner.cli.logging.StreamHandler') as handler_mock:
            CLI()

            self.assertTrue(handler_mock.call_count, 1)

    def test_disable(self):
        self.cli.disable()
        self.assertEqual(self.cli.logger.removeHandler.call_count, 1)

    def test_enable(self):
        self.cli.enable()
        self.assertEqual(self.cli.logger.addHandler.call_count, 1)

    def test_print_return_ok(self):
        self.cli.print_return(0)
        expected_calls = [call(logging.INFO, 'Return code: %d', 0)]
        self.assertCountEqual(self.cli.logger.log.call_args_list, expected_calls)

    def test_print_return_error(self):
        self.cli.print_return(1)
        expected_calls = [call(logging.ERROR, 'Return code: %d', 1)]
        self.assertCountEqual(self.cli.logger.log.call_args_list, expected_calls)

    def test_print_header(self):
        self.cli.print_header(foo=True, bar=1)
        msg = self.cli.logger.info.call_args[0][0]
        self.assertIn('Foo: True', msg)
        self.assertIn('Bar: 1', msg)

    def tearDown(self):
        pass
