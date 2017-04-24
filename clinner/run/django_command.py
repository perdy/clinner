import argparse  # noqa

try:
    from django.core.management.base import BaseCommand, CommandParser
except ImportError:
    BaseCommand = object
    CommandParser = None

__all__ = ['DjangoCommand']


class DjangoCommand(BaseCommand):
    """
    Wrapper that makes a Django command from a Main class, including parsers only for commands.
    """
    main_class = None

    def __init__(self, *args, **kwargs):
        self.help = self.main_class.description
        super(DjangoCommand, self).__init__(*args, **kwargs)
        self.command = self.main_class(parse_args=False)
        self.command.cli.disable()

    def add_arguments(self, parser):
        self.command._commands_arguments(parser=parser, parser_class=CommandParser)

    def handle(self, *args, **options):
        self.command.run(**options)
