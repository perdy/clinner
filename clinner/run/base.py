import argparse
import os
import subprocess
from abc import ABCMeta

from clinner.builder import Builder as CommandBuilder
from clinner.cli import cli
from clinner.command import command
from clinner.settings import settings

__all__ = ['MainMeta', 'BaseMain']


class MainMeta(ABCMeta):
    def __new__(mcs, name, bases, namespace):
        def inject(self):
            """
            Add all environment variables defined in all inject methods.
            """
            for method in [v for k, v in namespace.items() if k.startswith('inject_')]:
                method(self)

        def add_arguments(self, parser):
            """
            Add command line arguments to parser.

            :param parser: Parser.
            """
            for base in bases:
                if hasattr(base, 'add_arguments'):
                    getattr(base, 'add_arguments')(self, parser)

        namespace['inject'] = inject
        namespace['add_arguments'] = add_arguments
        return super(MainMeta, mcs).__new__(mcs, name, bases, namespace)


class BaseMain(metaclass=MainMeta):
    def __init__(self):
        self.builder = CommandBuilder()
        self.args = self.parse_arguments()

        # Load settings
        self.settings = self.args.settings or os.environ.get('CLINNER_SETTINGS')
        settings.build_from_module(self.args.settings)

        # Apply quiet mode
        if self.args.quiet:
            cli.disable()

        # Inject parameters related to current stage as environment variables
        self.inject()

    def parse_arguments(self):
        """
        command Line application arguments.
        """
        parser = argparse.ArgumentParser()

        self.add_arguments(parser)

        parser.add_argument('-s', '--settings',
                            help='Module or object with Clinner settings in format "package.module[:Object]"')
        parser.add_argument('-q', '--quiet', help='Quiet mode. No standard output other than executed application',
                            action='store_true')

        # Create subparser for each command
        subparsers = parser.add_subparsers(title='Commands', dest='command')
        for cmd_name, cmd in command.register.items():
            p = subparsers.add_parser(cmd_name, **cmd['parser'])
            for argument in cmd['arguments']:
                p.add_argument(*argument)

        parser.add_argument('args', help='Command args', nargs=argparse.REMAINDER, type=str)

        return parser.parse_args()

    def run_command(self, input_command, *args, **kwargs):
        """
        Run the given command, building it with arguments.

        :param input_command:
        :param args:
        :param kwargs:
        :return:
        """
        # Get list of commands
        commands = self.builder.build_command(input_command, *args, **kwargs)

        cli.logger.debug('Running commands:') if commands else None
        return_code = 0
        for c in commands:
            cli.logger.debug('- {}'.format((str(c))))
            # Run command
            p = subprocess.Popen(args=c)
            while p.returncode is None:
                try:
                    p.wait()
                except KeyboardInterrupt:
                    pass
            return_code = p.returncode

            # Break on non-zero exit code.
            if return_code != 0:
                return return_code

        return return_code

    def run(self):
        cli.print_header(command=self.args.command, settings=self.settings)

        return_code = self.run_command(self.args.command, *self.args.args)

        cli.print_return(return_code)
        return return_code

