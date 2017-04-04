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

Register
========
All commands will be registered in a :class:`clinner.command.CommandRegister` that can be accessed through
:attr:`command.register`. Each entry in this register is a dictionary with the fields declared at the beginning of this
section.

.. autoclass:: clinner.command.CommandRegister
    :members:
