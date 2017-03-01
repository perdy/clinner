import shlex
from typing import Callable, List

from clinner.command import command
from clinner.exceptions import WrongCommandError
from clinner.settings import settings

__all__ = ['builder']


class Builder:
    def __init__(self):
        # Load config
        self.default_args = {k: shlex.split(v) for k, v in settings.default_args.items()}
        self.bin = settings.bin

    def _get_method(self, name: str) -> Callable[..., List[List[str]]]:
        """
        Get self method given a name. If method isn't found, django_admin will be used as default return value.

        :param name: Method name.
        :return: Method itself.
        """
        try:
            return command.register[name]['callable']
        except KeyError:
            raise WrongCommandError(name)

    def build_command(self, command_name: str, *args, **kwargs) -> List[List[str]]:
        """
        Build command given his name and a list of args.

        :param command_name: command name.
        :param args: List of command args.
        :return: List of commands ready to be executed.
        """
        method = self._get_method(command_name)
        if not args:
            args = self.default_args.get(command_name, [])
        cmd = method(*args, **kwargs)

        return cmd


builder = Builder()
