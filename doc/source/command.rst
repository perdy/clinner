Commands
********

Command Decorator
=================
Commands are declared using a decorator to register given functions. Commands are functions with the follow parameters:

    func
        Function that will be called when command would be executed.

    command_type
        Type of the command, could be a *bash* or *python* command.

    args
        Parser arguments for this command.

    parser_opts
        Command subparser's keywords, such as description.

.. autoclass:: clinner.command.command
    :members:

How to use
----------
This decorator allows to be used as a common decorator without arguments, where default type (*python*) will be used:

.. code-block:: python

    @command
    def foobar(bar):
        pass

Or specifying the type:

.. code-block:: python

    @command(command_type=Type.SHELL)
    def foobar(bar):
        return [['cat', 'foobar']]

But also is possible to provide command line arguments, as expected by :meth:`argparse.ArgumentParser.add_argument`:

.. code-block:: python

    @command(args=((('-f', '--foo'), {'help': 'Foo argument that does nothing'}),
                   (('--bar',), {'action': 'store_true', 'help': 'Bar argument stored as True'})),
             parser_opts={'title': 'foobar_command', 'help': 'Help for foobar_command'})
    def foobar(*args, **kwargs):
        pass

For last, is possible to decorate functions or class methods:

.. code-block:: python

    class Foo:
        @staticmethod
        @command
        def bar():
            pass


Types
-----
Define the type of process to be executed by :class:`clinner.run.Main`.

Python
^^^^^^
Python function executed in a different process. Must implement the function itself.

Shell
^^^^^
List of shell commands executed in different processes. Each command must be a list of splitted command such as
returned from :func:`shlex.split`. As it can execute more than a single command, a list of lists should be returned.

Bash
^^^^
Alias for Shell.

Arguments
---------
Command line arguments are defined through *args* parameter of command decorator. This arguments can be defined using
the follow structure:

.. code-block:: python

    @command(args=(
        (('positionals',) {'help': 'Positional arguments', 'nargs': '+'}),
        (('-f', '--foo'), {'help': 'Foo argument', 'default': 'foo'}),
        (('--bar',), {'help': 'Bar argument', 'default': 1, 'type': int, 'choices': range(1, 6)}),
    ))
    def cmd(*args, **kwargs):
        pass

Also is possible to define args using a callable that receives the parser:

.. code-block:: python

    def add_arguments(parser):
        parser.add_argument('positionals', help='Positional arguments', nargs='+')
        parser.add_argument('-f', '--foo', help='Foo argument', default='foo')
        parser.add_argument('--bar', help='Bar argument', default=1, type=int, choices=range(1, 6))

    @command(args=add_arguments)
    def cmd(*args, **kwargs):
        pass

Parser options
--------------
It is possible to pass options to the command parser, such as *title*, *help*... These options should be passed through
*parser_opts* parameter of command decorator:

.. code-block:: python

    @command(parser_opts={'help': 'Command doing awesome things!'})
    def cmd(*args, **kwargs):
        pass

Register
========
All commands will be registered in a :class:`clinner.command.CommandRegister` that can be accessed through
:attr:`command.register`. Each entry in this register is a dictionary with the fields declared at the beginning of this
section.

.. autoclass:: clinner.command.CommandRegister
    :members:
