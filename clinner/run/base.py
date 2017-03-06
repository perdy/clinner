import argparse
import multiprocessing
import os
import subprocess
from abc import ABCMeta

from clinner.builder import Builder as CommandBuilder
from clinner.cli import cli
from clinner.command import command, Type
from clinner.exceptions import CommandTypeError
from clinner.settings import settings

__all__ = ['MainMeta', 'BaseMain']


class MainMeta(ABCMeta):
    def __new__(mcs, name, bases, namespace):  # noqa
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
        self.args, self.sub_args = self.parse_arguments()

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
            p = subparsers.add_parser(cmd_name, **cmd['parser'], add_help=False)
            for argument in cmd['arguments']:
                p.add_argument(*argument)

        # parser.add_argument('args', help='Command args', nargs=argparse.REMAINDER, type=str)

        return parser.parse_known_args()

    def run_python(self, cmd):
        """
        Run a python command in a different process.

        :param cmd: Python command.
        :return: Command return code.
        """
        cli.logger.debug('- {}'.format((str(cmd.__qualname__))))

        # Run command
        p = multiprocessing.Process(target=cmd)
        p.start()
        while p.exitcode is None:
            try:
                p.join()
            except KeyboardInterrupt:
                pass

        return p.exitcode

    def run_bash(self, cmd):
        """
        Run a bash command in a different process.

        :param cmd: Bash command.
        :return: Command return code.
        """
        cli.logger.debug('- {}'.format((str(cmd))))

        # Run command
        p = subprocess.Popen(args=cmd)
        while p.returncode is None:
            try:
                p.wait()
            except KeyboardInterrupt:
                pass

        return p.returncode

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
        for c, c_type in commands:
            if c_type == Type.python:
                self.run_python(c)
            elif c_type == Type.bash:
                self.run_bash(c)
            else:
                raise CommandTypeError(c_type)

            # Break on non-zero exit code.
            if return_code != 0:
                return return_code

        return return_code

    def run(self):
        cli.print_header(command=self.args.command, settings=self.settings)

        return_code = self.run_command(self.args.command, *self.sub_args)

        cli.print_return(return_code)
        return return_code
