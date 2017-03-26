import argparse
import os
from abc import ABCMeta, abstractmethod
from multiprocessing import Process
from subprocess import Popen

from clinner.builder import Builder
from clinner.cli import cli
from clinner.command import Type, command
from clinner.exceptions import CommandArgParseError, CommandTypeError
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
    def __init__(self, args=None):
        self.args, self.unknown_args = self.parse_arguments(args=args)
        self.settings = self.args.settings or os.environ.get('CLINNER_SETTINGS')

        # Inject parameters related to current stage as environment variables
        self.inject()

        # Load settings
        settings.build_from_module(self.args.settings)

        # Apply quiet mode
        if self.args.quiet:
            cli.disable()

    def _base_arguments(self, parser: 'argparse.ArgumentParser'):
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
        subparsers.required = True
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

    @abstractmethod
    def add_arguments(self, parser: argparse.ArgumentParser):
        pass

    def parse_arguments(self, args=None):
        """
        command Line application arguments.
        """
        parser = argparse.ArgumentParser(conflict_handler='resolve')

        # Call inner method that adds arguments from all classes (defined in metaclass)
        self._add_arguments(parser)

        return parser.parse_known_args(args=args)

    def run_python(self, cmd, *args, **kwargs):
        """
        Run a python command in a different process.

        :param cmd: Python command.
        :param args: List of args passed to Process.
        :param kwargs: Dict of kwargs passed to Process.
        :return: Command return code.
        """
        cli.logger.debug('- [Python] %s.%s', str(cmd.__module__), str(cmd.__qualname__))

        # Run command
        p = Process(target=cmd, *args, **kwargs)
        p.start()
        while p.exitcode is None:
            try:
                p.join()
            except KeyboardInterrupt:
                pass

        return p.exitcode

    def run_bash(self, cmd, *args, **kwargs):
        """
        Run a bash command in a different process.

        :param cmd: Bash command.
        :param args: List of args passed to Popen.
        :param kwargs: Dict of kwargs passed to Popen.
        :return: Command return code.
        """
        cli.logger.debug('- [Bash] %s', str(cmd))

        # Run command
        p = Popen(args=cmd, *args, **kwargs)
        while p.returncode is None:
            try:
                p.wait()
            except KeyboardInterrupt:
                pass

        return p.returncode

    def run_command(self, input_command, *args, **kwargs):
        """
        Run the given command, building it with arguments.

        :param input_command: Command to execute.
        :param args: List of args passed to run_<type> command.
        :param kwargs: Dict of kwargs passed to run_<type> command.
        :return: Command return code.
        """
        # Get list of commands
        commands, command_type = Builder.build_command(input_command, *self.unknown_args, **vars(self.args))

        cli.logger.debug('Running commands:') if commands else None
        return_code = 0
        for c in commands:
            if command_type == Type.python:
                return_code = self.run_python(c, *args, **kwargs)
            elif command_type == Type.bash:
                return_code = self.run_bash(c, *args, **kwargs)
            else:
                raise CommandTypeError(command_type)

            # Break on non-zero exit code.
            if return_code != 0:
                return return_code

        return return_code

    @abstractmethod
    def run(self, *args, **kwargs):
        pass
