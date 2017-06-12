import argparse
import os
from abc import ABCMeta, abstractmethod
from importlib import import_module
from subprocess import Popen

from clinner.builder import Builder
from clinner.cli import CLI
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

        def add_arguments(self, parser, parser_class=None):
            """
            Add command line arguments to parser.

            :param parser: Parser.
            :param parser_class: Parser class.
            """
            self._commands_arguments(parser, parser_class)

            for base in reversed(bases):
                if hasattr(base, 'add_arguments'):
                    getattr(base, 'add_arguments')(self, parser)

            if hasattr(self, 'add_arguments'):
                self.add_arguments(parser)

        namespace['inject'] = inject
        namespace['_add_arguments'] = add_arguments

        for command_fqn in namespace.get('commands', []):
            try:
                m, c = command_fqn.rsplit('.', 1)
                if c not in namespace:
                    module = import_module(m)
                    cmd = getattr(module, c)
                    namespace[c] = staticmethod(cmd)
            except (ValueError, ImportError, AttributeError):
                raise ImportError("Command not found '{}'".format(command_fqn))

        return super(MainMeta, mcs).__new__(mcs, name, bases, namespace)


class BaseMain(metaclass=MainMeta):
    commands = []
    description = None

    def __init__(self, args=None, parse_args=True):
        self.cli = CLI()
        self.args, self.unknown_args = argparse.Namespace(), []
        if parse_args:
            self.args, self.unknown_args = self.parse_arguments(args=args)
            self.settings = self.args.settings or os.environ.get('CLINNER_SETTINGS')

            # Inject parameters related to current stage as environment variables
            self.inject()

            # Load settings
            settings.build_from_module(self.args.settings)

            # Apply quiet mode
            if self.args.quiet:
                self.cli.disable()

    def _commands_arguments(self, parser: 'argparse.ArgumentParser', parser_class=None):
        """
        Add arguments for each command to parser.

        :param parser: Parser
        """
        # Create subparser for each command
        subparsers_kwargs = {'parser_class': lambda **kwargs: parser_class(self, **kwargs)} if parser_class else {}
        subparsers = parser.add_subparsers(title='Commands', dest='command', **subparsers_kwargs)
        subparsers.required = True
        for cmd_name, cmd in command.register.items():

            subparser_opts = cmd['parser']
            if cmd['type'] == Type.SHELL:
                subparser_opts['add_help'] = False

            p = subparsers.add_parser(cmd_name, **subparser_opts)
            if callable(cmd['arguments']):
                cmd['arguments'](p)
            else:
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
    def add_arguments(self, parser: 'argparse.ArgumentParser'):
        """
        Add to parser all necessary arguments for this Main.

        :param parser: Argument parser.
        """
        pass

    def parse_arguments(self, args=None, parser=None, parser_class=None):
        """
        command Line application arguments.
        """
        if parser is None:
            parser = argparse.ArgumentParser(description=self.description, conflict_handler='resolve')

        # Call inner method that adds arguments from all classes (defined in metaclass)
        self._add_arguments(parser, parser_class)

        return parser.parse_known_args(args=args)

    def run_python(self, cmd, *args, **kwargs):
        """
        Run a python command in a different process.

        :param cmd: Python command.
        :param args: List of args passed to Process.
        :param kwargs: Dict of kwargs passed to Process.
        :return: Command return code.
        """
        self.cli.logger.debug('- [Python] %s.%s', str(cmd.__module__), str(cmd.__qualname__))

        result = 0

        if not getattr(self.args, 'dry_run', False):
            # Run command
            result = cmd(*args, **kwargs)

        return result

    def run_shell(self, cmd, *args, **kwargs):
        """
        Run a shell command in a different process.

        :param cmd: Shell command.
        :param args: List of args passed to Popen.
        :param kwargs: Dict of kwargs passed to Popen.
        :return: Command return code.
        """
        self.cli.logger.debug('- [Shell] %s', ' '.join(cmd))

        result = 0

        if not getattr(self.args, 'dry_run', False):
            # Run command
            p = Popen(args=cmd, *args, **kwargs)
            while p.returncode is None:  # pragma: no cover
                try:
                    p.wait()
                except KeyboardInterrupt:
                    pass

            result = p.returncode

        return result

    def run_command(self, input_command, *args, **kwargs):
        """
        Run the given command, building it with arguments.

        :param input_command: Command to execute.
        :param args: List of args passed to run_<type> command.
        :param kwargs: Dict of kwargs passed to run_<type> command.
        :return: Command return code.
        """
        # Get list of commands
        commands, command_type = Builder.build_command(input_command, *args, **kwargs)

        self.cli.logger.debug('Running commands:') if commands else None
        return_code = 0
        for c in commands:
            if command_type == Type.PYTHON:
                return_code = self.run_python(c)
            elif command_type in (Type.SHELL, Type.SHELL_WITH_HELP):
                return_code = self.run_shell(c)
            else:  # pragma: no cover
                raise CommandTypeError(command_type)

            # Break on non-zero exit code.
            if return_code != 0:
                return return_code

        return return_code

    @abstractmethod
    def run(self, *args, **kwargs):
        pass
