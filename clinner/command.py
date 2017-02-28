from functools import partial, update_wrapper

from clinner.utils.collections import Register

__all__ = ['command']


class CommandRegister(Register):
    """
    Register for commands.
    """
    def register(self, func, *args, **kwargs):
        self[func.__name__] = {
            'callable': func,
            'arguments': args,
            'parser': kwargs,
        }


class command:  # noqa
    """
    Decorator to register the given functions in a register, along with their command line arguments.
    """
    register = CommandRegister()

    def __init__(self, func=None, *args, **kwargs):
        """
        Decorator that creates a Celery task of given function or class method and register it. This decorator allows
        to be used as a common decorator without arguments:

        @command
        def foobar(bar):
            pass

        But also is possible to provide command line arguments, as expected by argparse.ArgumentParser.add_argument:
        @command((('-f', '--foo'), {help='Foo argument that does nothing'}),
                 (('--bar',), {action='store_true', help='Bar argument stored as True'})
                 title='foobar_command', help='Help for foobar_command')
        def foobar(*args, **kwargs):
            pass

        For last, is possible to decorate functions or class methods:
        class Foo:
            @command
            def bar(self):
                pass

        :param func: Function or class method to be decorated.
        :param args: argparse.ArgumentParser.add_argument args.
        :param kwargs: argparse.ArgumentParser.add_subparser kwargs.
        """
        self.args = args
        self.kwargs = kwargs

        if func is not None and callable(func) and len(args) == 0 and len(kwargs) == 0:
            # Full initialization decorator
            self._decorate(func)
        else:
            # Partial initialization decorator
            self.func = None

    def _decorate(self, func, *args, **kwargs):
        self.func = func
        update_wrapper(self, func)

        self.register.register(func, *args, **kwargs)

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
                self._decorate(func=args[0], *self.args, **self.kwargs)
                return self
            else:
                raise ValueError('Decorator is not initialized')
