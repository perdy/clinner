from clinner.cli import cli
from clinner.run.base import BaseMain
from clinner.run.mixins import VaultMixin, HealthCheckMixin

__all__ = ['Main', 'HealthCheckMain', 'VaultMain']


class Main(BaseMain):
    def run(self):
        """
        Run specified command through system arguments.

        Arguments that have been parsed properly will be passed through **kwargs. Unknown arguments will be passed as a
        list of strings through *args.

        This method will print a header
        """
        cli.print_header(command=self.args.command, settings=self.settings)

        return_code = self.run_command(self.args.command, *self.unknown_args, **vars(self.args))

        cli.print_return(return_code)
        return return_code


class HealthCheckMain(HealthCheckMixin, Main):
    """
    Main class with health check behavior.
    """
    def health_check(self):
        return True


class VaultMain(VaultMixin, Main):
    """
    Main class with vault behavior that injects variables into environment.
    """
    pass
