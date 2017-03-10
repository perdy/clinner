import argparse
import multiprocessing
import os
import subprocess
from abc import ABCMeta, abstractmethod

from clinner.builder import Builder as CommandBuilder
from clinner.cli import cli
from clinner.command import command, Type
from clinner.exceptions import CommandTypeError, CommandArgParseError
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
            self._base_arguments(parser)

            for base in reversed(bases):
                if hasattr(base, 'add_arguments'):
                    getattr(base, 'add_arguments')(self, parser)

            if hasattr(self, 'add_arguments'):
                self.add_arguments(parser)

        namespace['inject'] = inject
        namespace['_add_arguments'] = add_arguments
        return super(MainMeta, mcs).__new__(mcs, name, bases, namespace)


class BaseMain(metaclass=MainMeta):
    def __init__(self):
        self.builder = CommandBuilder()
        self.args, self.unknown_args = self.parse_arguments()
        self.settings = self.args.settings or os.environ.get('CLINNER_SETTINGS')

        # Inject parameters related to current stage as environment variables
        self.inject()

        # Load settings
        settings.build_from_module(self.args.settings)

        # Apply quiet mode
        if self.args.quiet:
            cli.disable()

    def _base_arguments(self, parser: argparse.ArgumentParser):
        """
        Add arguments to parser.

        :param parser: Parser
        """
        parser.add_argument('-s', '--settings',
                            help='Module or object with Clinner settings in format "package.module[:Object]"')
        parser.add_argument('-q', '--quiet', help='Quiet mode. No standard output other than executed application',
                            action='store_true')

        # Create subparser for each command
        subparsers = parser.add_subparsers(title='Commands', dest='command')
        for cmd_name, cmd in command.register.items():

            subparser_opts = cmd['parser']
            if cmd['type'] == Type.bash:
                subparser_opts['add_help'] = False

            p = subparsers.add_parser(cmd_name, **subparser_opts)
            for argument in cmd['arguments']:
                try:
                    if len(argument) == 2:
                        args, kwargs = argument
                    elif len(argument) == 1:
                        args = argument[0]
                        kwargs = {}
                    else:
                        args, kwargs = None, None

                    assert isinstance(args, (tuple, list))
                    assert isinstance(kwargs, dict)
                except AssertionError:
                    raise CommandArgParseError(str(argument))
                else:
                    p.add_argument(*args, **kwargs)

    def parse_arguments(self):
        """
        command Line application arguments.
        """
        parser = argparse.ArgumentParser(conflict_handler='resolve')

        # Call inner method that adds arguments from all classes (defined in metaclass)
        self._add_arguments(parser)

        return parser.parse_known_args()

    def run_python(self, cmd):
        """
        Run a python command in a different process.

        :param cmd: Python command.
        :return: Command return code.
        """
        cli.logger.debug('- [Python] %s.%s', str(cmd.__module__), str(cmd.__qualname__))

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
        cli.logger.debug('- [Bash] %s', str(cmd))

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
        commands, command_type = self.builder.build_command(input_command, *args, **kwargs)

        cli.logger.debug('Running commands:') if commands else None
        return_code = 0
        for c in commands:
            if command_type == Type.python:
                self.run_python(c)
            elif command_type == Type.bash:
                self.run_bash(c)
            else:
                raise CommandTypeError(command_type)

            # Break on non-zero exit code.
            if return_code != 0:
                return return_code

        return return_code

    @abstractmethod
    def run(self):
        pass
