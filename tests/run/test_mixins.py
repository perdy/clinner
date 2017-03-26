from unittest.case import TestCase

from clinner.run import BaseMain


class Main(BaseMain):
    def add_arguments(self, parser: 'argparse.ArgumentParser'):
        pass

    def run(self):
        pass


class BaseMainTestCase(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass


class MainTestCase(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass


class HealthChechMixin(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

