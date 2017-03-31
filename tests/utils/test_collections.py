from unittest.case import TestCase

from clinner.utils.collections import Register


class RegisterTestCase(TestCase):
    def setUp(self):
        self.register = Register()

    def test_set_item(self):
        self.register['foo'] = 'bar'

        self.assertIn('foo', self.register)
        self.assertEqual('bar', self.register['foo'])

    def test_set_item_twice(self):
        self.register['foo'] = 'bar'

        self.assertIn('foo', self.register)
        self.assertEqual('bar', self.register['foo'])

        with self.assertRaises(KeyError):
            self.register['foo'] = 'foobar'

    def test_str(self):
        self.register['foo'] = 'bar'
        expected_str = "{'foo': 'bar'}"

        self.assertEqual(str(self.register), expected_str)

    def test_repr(self):
        self.register['foo'] = 'bar'
        expected_repr = "{'foo': 'bar'}"

        self.assertEqual(repr(self.register), expected_repr)

    def tearDown(self):
        pass
