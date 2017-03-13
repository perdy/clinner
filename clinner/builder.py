import shlex
from functools import partial, update_wrapper
from typing import Callable, List, Any, Dict, Tuple, Union

from clinner.command import command, Type as CommandType
from clinner.exceptions import CommandTypeError
from clinner.settings import settings

__all__ = ['Builder']


class Builder:
    """
    Helper for build commands stored in register.
    """
    @staticmethod
    def _get_method(cmd: Dict[str, Any]) -> Callable[..., List[List[str]]]:
        """
        Get self method given a name. If method isn't found, django_admin will be used as default return value.

        :param cmd: Command registered.
        :return: Method itself.
        """
        method = cmd['callable']

        # Is a class method
        if cmd['instance']:
            method = partial(method, cmd['instance'])

        return method

    @staticmethod
    def _build_bash_command(method, *args, **kwargs) -> List[List[str]]:
        """
        Build a bash command using given method, args and kwargs. Bash commands should return a list of bash commands
        split by shlex.

        :param method: Command callable.
        :param args: List of command args.
        :param kwargs: Dict of command kwargs.
        :return: List of commands ready to be executed.
        """
        return method(*args, **kwargs)

    @staticmethod
    def _build_python_command(method, *args, **kwargs) -> List[Callable]:
        """
        Build a python command using given method, args and kwargs. Python commands will return a python's callable
        partialized with current args and kwargs

        :param method: Command callable.
        :param args: List of command args.
        :param kwargs: Dict of command kwargs.
        :return: List of commands ready to be executed.
        """
        cmd = partial(method, *args, **kwargs)
        update_wrapper(cmd, method)
        return [cmd]

    @staticmethod
    def build_command(command_name: str, *args, **kwargs) -> Tuple[List[Union[List[str], Callable]], CommandType]:
        """
        Build command given his name and a list of args.

        :param command_name: command name.
        :param args: List of command args.
        :param kwargs: Dict of command kwargs.
        :return: List of commands ready to be executed.
        """
        # Get registered command
        cmd = command.register[command_name]

        # Get command callable
        method = cmd['callable']
        command_type = cmd['type']

        # Get default args if necessary
        if not args:
            try:
                args = shlex.split(settings.default_args[command_name])
            except KeyError:
                args = []

        if command_type == CommandType.python:
            built = Builder._build_python_command(method, *args, **kwargs)
        elif command_type == CommandType.bash:
            built = Builder._build_bash_command(method, *args, **kwargs)
        else:
            raise CommandTypeError(command_type)

        return built, command_type
