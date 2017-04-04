Settings
********

Clinner settings can be specified through **CLINNER_SETTINGS** environment variable or using ``-s`` or ``--settings``
command line flags during invocation. The format to specify settings module or class should be either ``package.module``
or ``package.module:Class``.

Default Arguments
=================

Default arguments for commands. Let a command ``foo`` declared:

.. code-block:: python

    default_args = {
        'foo': ['-v', '--bar', 'foobar'],
    }
