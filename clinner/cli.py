import logging
from collections import OrderedDict
from logging import StreamHandler

__all__ = ['cli']


class CLI:
    """
    command Line Interface helpers, such as predefined styles for different type of messages, headers, etc.
    """
    SEP = '-' * 70

    def __init__(self):
        try:
            import colorlog
            self.handler = colorlog.StreamHandler()
            self.handler.setFormatter(colorlog.ColoredFormatter(
                '%(log_color)s%(message)s',
                datefmt=None,
                reset=True,
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white',
                },
                style='%'
            ))
        except ImportError:
            #  Default to basic logging
            self.handler = StreamHandler()

        self.logger = logging.getLogger('cli')
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)

    def disable(self):
        self.logger.removeHandler(self.handler)

    def enable(self):
        self.logger.addHandler(self.handler)

    def print_return(self, code: int):
        if code == 0:
            self.logger.info('Return code: 0')
        else:
            self.logger.error('Return code: {:d}'.format(code))

    def print_header(self, **kwargs):
        fields = OrderedDict(sorted(kwargs.items(), key=lambda x: x[0]))

        fmt = '{:<%d} {}' % (max([len(x) for x in fields.keys()]) + 5,)
        header_lines = [self.SEP]
        for k, v in fields.items():
            header_lines.append(fmt.format(k.capitalize() + ':', v))
        header_lines.append(self.SEP)

        self.logger.info('\n'.join(header_lines))


cli = CLI()
