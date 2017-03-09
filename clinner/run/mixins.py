import os
import time
from abc import ABCMeta, abstractmethod
from random import random

import hvac

from clinner.cli import cli
from clinner.settings import settings

__all__ = ['VaultMixin', 'HealthCheckMixin']


class VaultMixin:
    def inject_vault_variables(self):
        """
        Get app and user id and injects all variables defined at Vault secret as environment variables.
        """
        if settings.vault:
            vc = hvac.Client(url=settings.vault['url'])

            if 'app_id' in settings.vault and 'user_id' in settings.vault:
                cli.logger.debug('Vault auth using AppID')
                vc.auth_app_id(settings.vault['app_id'], settings.vault['user_id'])
            elif 'role_id' in settings.vault and 'secret_id' in settings.vault:
                cli.logger.debug('Vault auth using AppRole')
                vc.auth_approle(settings.vault['role_id'], settings.vault['secret_id'])
            else:
                cli.logger.warning('Vault authentication parameters not provided')

            if vc.is_authenticated():
                secrets = vc.read(settings.vault['secrets_path'])
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
