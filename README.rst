=======
Clinner
=======

:Version: 0.2.0
:Status: Production/Stable
:Author: José Antonio Perdiguero López

Command Line Interface builder that helps creating an entry point for your application.


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

Vault
-----

Vault arguments to retrieve secrets and inject them as environment variables:

.. code:: python
    vault = {
        'url': 'http://vaulturl',
        'secrets_path': 'vault_secrets_path_to_retrieve',
        'app_id_path': '/path/to/app_id_file',
        'user_id_path': '/path/to/user_id_file',
    }

Example
=======

Full code example:

.. code:: python
    import os
    import shlex
    import sys

    from clinner.command import command, Type as CommandType
    from clinner.run.main import Main


    @command(command_type=CommandType.bash
             args=(('-i', '--input'),
                   ('-o', '--output')))
    def foo(*args, **kwargs):
        """List of foo commands"""
        ls_cmd = shlex.split('ls')
        wc_cmd = shlex.split('wc')
        wc_cmd += [kwargs['input'], kwargs['output']]

        return [ls_cmd, wc_cmd]


    @command(command_type=CommandType.python)
    def bar(*args, **kwargs):
        """Do a bar."""
        return True


    if __name__ == '__main__':
        sys.exit(Main().run())
