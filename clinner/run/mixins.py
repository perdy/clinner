import os
import time
from abc import abstractmethod, ABCMeta
from random import random

from clinner import vault
from clinner.cli import cli

from clinner.settings import settings

__all__ = ['VaultMixin', 'HealthCheckMixin']


class VaultMixin:
    def inject_vault_variables(self):
        """
        Get app and user id and injects all variables defined at Vault secret as environment variables.
        """
        if settings.vault:
            try:
                with open(settings.vault['app_id_path']) as f:
                    app_id = f.readline()
            except FileNotFoundError:
                app_id = None

            try:
                with open(settings.vault['user_id_path']) as f:
                    user_id = f.readline()
            except FileNotFoundError:
                user_id = None

            vc = vault.Client(settings.vault['url'], app_id, user_id)
            if vc.connected:
                secrets = vc.get_secret(settings.vault['secrets_path'])
                os.environ.update(secrets)
            else:
                cli.logger.warning('Vault client is not connected')


class HealthCheckMixin(metaclass=ABCMeta):
    def add_arguments(self, parser):
        parser.add_argument('-r', '--retry', help='Health check retries before run command. Disabled with 0, max 5.',
                            type=int)

    @abstractmethod
    def health_check(self):
        """
        Does a health check.

        :return: True if health check was successful. False otherwise.
        """
        return True

    def _health_check(self):
        """
        Does a health check and retry using exponential backoff if it fails.

        :return: True if health check was successful. False otherwise.
        """
        if self.args.retry:
            health = False
            cli.logger.info('Performing healthcheck...')
            timeout = random()

            for i in (i for i in range(self.args.retry) if not health):
                if self.health_check():
                    cli.logger.warning('Health check failed, retrying ({}/{})'.format(i + 1, self.args.retry))
                    time.sleep(timeout)
                    timeout *= 2.
                else:
                    # Healthcheck successful
                    health = True

            if not health:
                cli.logger.error('Retry attempts exceeded, health check failed')
        else:
            health = True

        return health

    def run(self):
        cli.print_header(command=self.args.command, settings=self.settings)

        if self._health_check():
            return_code = self.run_command(self.args.command, *self.unknown_args, **vars(self.args))
        else:
            return_code = 1

        cli.print_return(return_code)
        return return_code
