from clinner.run.base import BaseMain
from clinner.run.mixins import VaultMixin, HealthCheckMixin

__all__ = ['Main', 'main']


def main():
    return Main().run()


class Main(BaseMain, HealthCheckMixin, VaultMixin):
    def health_check(self):
        return True
