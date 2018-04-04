from unittest.mock import patch

from clinner.inputs import bool_input, choices_input, default_input


class TestCaseBoolInput:
    def test_default(self):
        with patch('clinner.inputs.input', return_value=''):
            result = bool_input('Foo')

        assert result is True

    def test_yes(self):
        with patch('clinner.inputs.input', return_value='y'):
            result = bool_input('Foo')

        assert result is True

    def test_no(self):
        with patch('clinner.inputs.input', return_value='n'):
            result = bool_input('Foo')

        assert result is False

    def test_wrong(self):
        with patch('clinner.inputs.input', side_effect=['wrong', 'y']):
            result = bool_input('Foo')

        assert result is True


class TestCaseChoicesInput:
    def test_right(self):
        with patch('clinner.inputs.input', return_value='0'):
            result = choices_input('Foo', ['foo', 'bar'])

        assert result == 'foo'

    def test_wrong(self):
        with patch('clinner.inputs.input', side_effect=['3', '1']):
            result = choices_input('Foo', ['foo', 'bar'])

        assert result == 'bar'


class TestCaseDefaultInput:
    def test_right(self):
        with patch('clinner.inputs.input', return_value='foo'):
            result = default_input('Foo', 'bar')

        assert result == 'foo'

    def test_default(self):
        with patch('clinner.inputs.input', return_value=''):
            result = default_input('Foo', 'bar')

        assert result == 'bar'

    def test_empty_default(self):
        with patch('clinner.inputs.input', return_value=''):
            result = default_input('Foo')

        assert result == ''
