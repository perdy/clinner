import argparse
import logging
import os
import signal
from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from importlib import import_module
from subprocess import Popen

from clinner.builder import Builder
from clinner.cli import CLI
from clinner.command import Type, command
from clinner.exceptions import CommandArgParseError, CommandTypeError
from clinner.settings import settings

__all__ = ["MainMeta", "BaseMain"]


class MainMeta(ABCMeta):
    def __new__(mcs, name, bases, namespace):  # noqa
        def inject(self):
            """
            Add all environment variables defined in all inject methods.
            """
            # Gather inject methods from bases and current class_dict
            methods = {k: v for b in bases for k, v in b.__dict__.items() if k.startswith("inject_")}
            methods.update({k: v for k, v in namespace.items() if k.startswith("inject_")})

            for method_name, method in methods.items():
                method(self)

        def add_arguments(self, parser, parser_class=None):
            """
            Add command line arguments to parser.

            :param parser: Parser.
            :param parser_class: Parser class.
            """
            self._commands_arguments(parser, parser_class)

            for base in reversed(bases):
                if hasattr(base, "add_arguments"):
                    getattr(base, "add_arguments")(self, parser)

            if hasattr(self, "add_arguments"):
                self.add_arguments(parser)

        namespace["inject"] = inject
        namespace["_add_arguments"] = add_arguments

        cmds = {}
        for command_fqn in namespace.get("commands", []):
            try:
                m, c = command_fqn.rsplit(".", 1)
                if c not in namespace:
                    getattr(import_module(m), c)
                    cmds[c] = command.register[c]
            except ValueError:
                cmds[command_fqn] = command.register[command_fqn]
            except (ImportError, AttributeError):
                raise ImportError("Command not found '{}'".format(command_fqn))

        namespace["_commands"] = OrderedDict(sorted(cmds.items(), key=lambda t: t[0])) if cmds else None

        return super(MainMeta, mcs).__new__(mcs, name, bases, namespace)


class BaseMain(metaclass=MainMeta):
    commands = []
    description = None

    def __init__(self, args=None, parse_args=True):
        self.args, self.unknown_args = argparse.Namespace(), []
        self.cli = CLI()
        if parse_args:
            self.args, self.unknown_args = self.parse_arguments(args=args)

            # Set logging verbosity
            if self.args.quiet:
                self.cli.disable()
            elif self.args.verbose == 1:
                self.cli.set_level(logging.INFO)
            elif self.args.verbose >= 2:
                self.cli.set_level(logging.DEBUG)
            else:  # Default log level
                self.cli.set_level(logging.WARNING)

            # Inject parameters related to current stage as environment variables
            self.inject()

            # Get settings from args or envvar
            self.settings = self.args.settings or os.environ.get("CLINNER_SETTINGS")

            # Load settings
            settings.build_from_module(self.settings)

    def _commands_arguments(self, parser: "argparse.ArgumentParser", parser_class=None):
        """
        Add arguments for each command to parser.

        :param parser: Parser
        """
        # Create subparser for each command
        subparsers_kwargs = {"parser_class": lambda **kwargs: parser_class(self, **kwargs)} if parser_class else {}
        subparsers = parser.add_subparsers(title="Commands", dest="command", **subparsers_kwargs)
        subparsers.required = True

        cmds = self._commands if self._commands is not None else command.register
        for cmd_name, cmd in cmds.items():
            subparser_opts = cmd["parser"]
            if cmd["type"] == Type.SHELL:
                subparser_opts["add_help"] = False

            p = subparsers.add_parser(cmd_name, **subparser_opts)
            if callable(cmd["arguments"]):
                cmd["arguments"](p)
            else:
                for argument in cmd["arguments"]:
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
    def add_arguments(self, parser: "argparse.ArgumentParser"):
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
            parser = argparse.ArgumentParser(description=self.description, conflict_handler="resolve")

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
        self.cli.logger.debug("- [python] %s.%s", str(cmd.__module__), str(cmd.__qualname__))

        result = 0

        if not getattr(self.args, "dry_run", False):
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
        self.cli.logger.info("[shell] %s", " ".join(cmd))

        result = 0

        if not getattr(self.args, "dry_run", False):
            # Run command
            p = Popen(args=cmd, *args, **kwargs)
            while p.returncode is None:  # pragma: no cover
                try:
                    p.wait()
                except KeyboardInterrupt:
                    self.cli.logger.info("Soft quit signal received, waiting the process to stop")
                    p.send_signal(signal.SIGINT)
                    try:
                        p.wait()
                    except KeyboardInterrupt:
                        self.cli.logger.info("Hard quit signal received, killing the process immediately")
                        p.send_signal(signal.SIGKILL)
                        p.wait(timeout=3)

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

        self.cli.print_header(**kwargs)
        self.cli.print_commands_list(commands, command_type)

        return_code = 0
        for c in commands:
            if command_type == Type.PYTHON:
                return_code = self.run_python(c)
            elif command_type in (Type.SHELL, Type.SHELL_WITH_HELP):
                return_code = self.run_shell(c)
            else:  # pragma: no cover
                raise CommandTypeError(command_type)

            self.cli.print_return(return_code)

            # Break on non-zero exit code.
            if return_code != 0:
                return return_code

        return return_code

    @abstractmethod
    def run(self, *args, **kwargs):
        pass
