from clinner.cli import cli
from clinner.run.base import BaseMain
from clinner.run.mixins import HealthCheckMixin

__all__ = ['Main', 'HealthCheckMain']


class Main(BaseMain):
    def run(self):
        """
        Run specified command through system arguments.

        Arguments that have been parsed properly will be passed through **kwargs. Unknown arguments will be passed as a
        list of strings through *args.

        This method will print a header and the return code.
        """
        cli.print_header(command=self.args.command, settings=self.settings)

        return_code = self.run_command(self.args.command, *self.unknown_args, **vars(self.args))

        cli.print_return(return_code)
        return return_code


class HealthCheckMain(HealthCheckMixin, BaseMain):
    """
    Main class with health check behavior.
    """
    pass
