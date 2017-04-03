Commands
========
Commands are declared using a decorator to register given functions. Commands are functions with the follow parameters:

    func
        Function that will be called when command would be executed.

    command_type
        Type of the command, could be a *bash* or *python* command.

    args
        Parser arguments for this command.

    parser_opts
        Command subparser's keywords, such as description.

This decorator allows to be used as a common decorator without arguments, where default type (*python*) will be used:

.. code-block:: python

    @command
    def foobar(bar):
        pass

Or specifying the type:

.. code-block:: python

    @command(command_type=Type.python)
    def foobar(bar):
        pass

But also is possible to provide command line arguments, as expected by argparse.ArgumentParser.add_argument:

.. code-block:: python

    @command(args=((('-f', '--foo'), {'help': 'Foo argument that does nothing'}),
                   (('--bar',), {'action': 'store_true', 'help': 'Bar argument stored as True'})),
             parser_opts={'title': 'foobar_command', 'help': 'Help for foobar_command'})
    def foobar(*args, **kwargs):
        pass

All commands will be registered in a command register that can be accessed through ``command.register``. Each entry in
this register is a dictionary with the fields declared at the beginning of this section.
