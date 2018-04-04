import logging
from unittest.mock import MagicMock, call, patch

import pytest

from clinner.cli import CLI


class TestCaseCLI:
    @pytest.fixture
    def cli(self):
        cli = CLI()
        cli.logger = MagicMock()
        return cli

    def test_init_with_colorlog(self):
        with patch('clinner.cli._colorlog', True), patch('colorlog.StreamHandler') as handler_mock:
            CLI()

            assert handler_mock.call_count == 1
            assert handler_mock.return_value.setFormatter.call_count == 1

    def test_init_without_colorlog(self):
        with patch('clinner.cli._colorlog', False), patch('clinner.cli.logging.StreamHandler') as handler_mock:
            CLI()

            assert handler_mock.call_count == 1

    def test_disable(self, cli):
        cli.disable()
        assert cli.logger.removeHandler.call_count == 1

    def test_enable(self, cli):
        cli.enable()
        assert cli.logger.addHandler.call_count == 1

    def test_set_level(self, cli):
        cli.set_level(logging.INFO)
        assert cli.logger.setLevel.call_args_list == [call(logging.INFO)]

    def test_print_return_ok(self, cli):
        cli.print_return(0)
        expected_calls = [call(logging.INFO, 'Return code: %d', 0)]
        assert cli.logger.log.call_args_list == expected_calls

    def test_print_return_none(self, cli):
        cli.print_return(None)
        expected_calls = [call(logging.INFO, 'Return code: %d', 0)]
        assert cli.logger.log.call_args_list == expected_calls

    def test_print_return_error(self, cli):
        cli.print_return(1)
        expected_calls = [call(logging.ERROR, 'Return code: %d', 1)]
        assert cli.logger.log.call_args_list == expected_calls

    def test_print_header(self, cli):
        cli.print_header(foo=True, bar=1)
        msg = cli.logger.info.call_args[0][0]
        assert 'Foo: True' in msg
        assert 'Bar: 1' in msg
