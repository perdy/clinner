from enum import Enum
from functools import partial, update_wrapper

from typing import Any, Callable, Dict, Tuple

from clinner.exceptions import WrongCommandError

__all__ = ['command', 'Type']


class Type(Enum):
    PYTHON = 'python'
    SHELL = 'shell'
    BASH = SHELL
    SHELL_WITH_HELP = 'shell_with_help'
    BASH_WITH_HELP = SHELL_WITH_HELP


class CommandRegister(dict):
    """
    Register for commands.
    """

    def register(self, func: Callable, command_type: Type, arguments: Tuple[Tuple[str], Dict[str, Any]],
                 parser: Dict[str, Any]):
        self[func.__name__] = {
            'callable': func,
            'type': command_type,
            'arguments': arguments,
            'parser': parser,
        }

    def __getitem__(self, item):
        if item not in self:
            raise WrongCommandError(item)

        return dict.__getitem__(self, item)


class command:  # noqa
    """
    Decorator to register the given functions in a register, along with their command line arguments.
    """
    register = CommandRegister()

    def __init__(self, func=None, command_type=Type.PYTHON, args=None, parser_opts=None):
        """
        Decorator to register given functions in a register. This decorator allows to be used as a common decorator
        without arguments:

        @command
        def foobar(bar):
            pass

        But also is possible to provide command line arguments, as expected by argparse.ArgumentParser.add_argument:
        @command((('-f', '--foo'), {help='Foo argument that does nothing'}),  # Command argument
                 (('--bar',), {action='store_true', help='Bar argument stored as True'})  # Another command argument
                 title='foobar_command', help='Help for foobar_command')  # Parser parameters
        def foobar(*args, **kwargs):
            pass

        @command(args=((('-f', '--foo'), {'help': 'Foo argument that does nothing'}),
                       (('--bar',), {'action': 'store_true', 'help': 'Bar argument stored as True'})),
                 parser_opts={'title': 'foobar_command', 'help': 'Help for foobar_command'})
        def foobar(*args, **kwargs):
            pass

        For last, is possible to decorate functions or class methods:
        class Foo:
            @staticmethod
            @command
            def bar():
                pass

        :param func: Function or class method to be decorated.
        :param args: argparse.ArgumentParser.add_argument args.
        :param parser_opts: argparse.ArgumentParser.add_subparser kwargs.
        """
        self.args = args or ()
        self.kwargs = parser_opts or {}
        self.command_type = command_type

        if func is not None and callable(func):
            # Full initialization decorator
            self._decorate(func=func, command_type=self.command_type, args=self.args, parse_opts=self.kwargs)
        else:
            # Partial initialization decorator
            self.func = None

    def _decorate(self, func, command_type, args, parse_opts):
        self.func = func
        update_wrapper(self, func)

        self.register.register(self, command_type, args, parse_opts)

    def __get__(self, instance, owner=None):
        """
        Make it works with functions and methods.
        """
        return partial(self.__call__, instance)

    def __call__(self, *args, **kwargs):
        """
        Call function. If decorator is not fully initialized, initialize it.
        """
        if self.func:
            # Decorator behavior
            return self.func(*args, **kwargs)
        else:
            # Decorator is not initialized and now is giving the function to be decorated
            if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
                self._decorate(func=args[0], command_type=self.command_type, args=self.args, parse_opts=self.kwargs)
                return self
            else:
                raise ValueError('Decorator is not initialized')
