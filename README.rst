*******
Clinner
*******
|build-status| |coverage| |version|

:Version: 1.6.2
:Status: Production/Stable
:Author: José Antonio Perdiguero López

Command Line Interface builder that helps creating an entry point for your application.

Check full `Clinner documentation`_.

Quick start
===========
1. Install this package using pip:

.. code:: bash

    pip install clinner

2. Create a command

.. code:: python

    from clinner.command import command

    @command
    def foo(*args, **kwargs):
        return True

3. Create a main file:

.. code:: python

    from clinner.run.main import Main

    if __name__ == '__main__':
        sys.exit(Main().run())

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

.. code:: python

    @command
    def foobar(bar):
        pass

Or specifying the type:

.. code:: python

    @command(command_type=Type.python)
    def foobar(bar):
        pass

But also is possible to provide command line arguments, as expected by argparse.ArgumentParser.add_argument:

.. code:: python

    @command(args=((('-f', '--foo'), {'help': 'Foo argument that does nothing'}),                   # Command argument
                   (('--bar',), {'action': 'store_true', 'help': 'Bar argument stored as True'})),  # Another argument
             parser_opts={'title': 'foobar_command', 'help': 'Help for foobar_command'})            # Parser parameters
    def foobar(*args, **kwargs):
        pass

All commands will be registered in a command register that can be accessed through ``command.register``. Each entry in
this register is a dictionary with the fields declared at the beginning of this section.

Main
====
A main class is defined to ease the creation of command line applications. This class follows the process:

1. Create a parser using ``argparse.ArgumentParser`` for the application:

    a) Calling all ``add_arguments(parser)`` methods from all super classes, e.g: ``clinner.mixins.HealthCheckMixin``.
    b) Addding a subparser for each command with their specific arguments.

2. Parse arguments using the argument parser created previously.

3. Inject variables into environment calling all super classes methods whose name starts with ``inject_``.

4. Load settings module from **CLINNER_SETTINGS** environment variable. More details below.


Settings
========
Clinner settings can be specified through **CLINNER_SETTINGS** environment variable or using ``-s`` or ``--settings``
command line flags during invocation. The format to specify settings module or class should be either ``package.module``
or ``package.module:Class``.

Default Arguments
-----------------
Default arguments for commands. Let a command ``foo`` declared:

.. code:: python

    default_args = {
        'foo': ['-v', '--bar', 'foobar'],
    }

Examples
========
Some Clinner examples.

Simple Main
-----------
Example of a simple main with two defined commands *foo* and *bar*.

.. code-block:: python

    #!/usr/bin/env python
    import os
    import shlex
    import sys

    from clinner.command import command, Type as CommandType
    from clinner.run.main import Main


    @command(command_type=CommandType.SHELL
             args=(('-i', '--input'),
                   ('-o', '--output')))
    def foo(*args, **kwargs):
        """List of foo commands"""
        ls_cmd = shlex.split('ls')
        wc_cmd = shlex.split('wc')
        wc_cmd += [kwargs['input'], kwargs['output']]

        return [ls_cmd, wc_cmd]


    @command(command_type=CommandType.PYTHON)
    def bar(*args, **kwargs):
        """Do a bar."""
        return True


    if __name__ == '__main__':
        sys.exit(Main().run())

Builder Main
------------
Example of main module with build utilities such as unit tests, lint, sphinx doc, tox and dist packaging:

.. code-block:: python

    #!/usr/bin/env python
    import sys

    from clinner.run import Main


    class Build(Main):
        commands = (
            'clinner.run.commands.nose.nose',
            'clinner.run.commands.prospector.prospector',
            'clinner.run.commands.sphinx.sphinx',
            'clinner.run.commands.tox.tox',
            'clinner.run.commands.dist.dist',
        )


    def main():
        return Build().run()


    if __name__ == '__main__':
        sys.exit(main())


.. _Clinner documentation: http://clinner.readthedocs.io
.. |build-status| image:: https://travis-ci.org/PeRDy/clinner.svg?branch=master
    :alt: build status
    :scale: 100%
    :target: https://travis-ci.org/PeRDy/clinner
.. |coverage| image:: https://coveralls.io/repos/github/PeRDy/clinner/badge.svg
    :alt: coverage
    :scale: 100%
    :target: https://coveralls.io/github/PeRDy/clinner
.. |version| image:: https://badge.fury.io/py/clinner.svg
    :alt: version
    :scale: 100%
    :target: https://badge.fury.io/py/clinner
