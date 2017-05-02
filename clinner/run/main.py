import argparse  # noqa

from clinner.run.base import BaseMain
from clinner.run.mixins import HealthCheckMixin

__all__ = ['Main', 'HealthCheckMain']


class Main(BaseMain):
    def add_arguments(self, parser: 'argparse.ArgumentParser'):
        """
        Add to parser all necessary arguments for this Main.

        :param parser: Argument parser.
        """
        parser.add_argument('-s', '--settings',
                            help='Module or object with Clinner settings in format "package.module[:Object]"')
        parser.add_argument('-q', '--quiet', help='Quiet mode. No standard output other than executed application',
                            action='store_true')
        parser.add_argument('--dry-run', action='store_true',
                            help='Dry run. Skip commands execution, useful to check which commands will be executed '
                                 'and execution order')

    def run(self, *args, **kwargs):
        """
        Run specified command through system arguments.

        Arguments that have been parsed properly will be passed through \**kwargs. Unknown arguments will be passed as a
        list of strings through \*args.

        This method will print a header and the return code.
        """
        cmd_args = self.unknown_args if not args else args

        cmd_kwargs = vars(self.args)
        cmd_kwargs.update(kwargs)

        command = cmd_kwargs['command']
        settings = cmd_kwargs['settings']

        self.cli.print_header(command=command, settings=settings)

        return_code = self.run_command(command, *cmd_args, **cmd_kwargs)

        self.cli.print_return(return_code)
        return return_code


class HealthCheckMain(HealthCheckMixin, Main):
    """
    Main class with health check behavior.
    """
    pass
