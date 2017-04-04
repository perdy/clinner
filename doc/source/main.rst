Main
****

A main class is defined to ease the creation of command line applications. This class follows the process:

1. Create a parser using ``argparse.ArgumentParser`` for the application:

    a) Calling all ``add_arguments(parser)`` methods from all super classes, e.g: ``clinner.mixins.HealthCheckMixin``.
    b) Addding a subparser for each command with their specific arguments.

2. Parse arguments using the argument parser created previously.

3. Inject variables into environment calling all super classes methods whose name starts with ``inject_``.

4. Load settings module from **CLINNER_SETTINGS** environment variable. More details below.

.. autoclass:: clinner.run.main.Main
    :members:

Commands
========

All commands previously loaded will be available to use by the main class but also there is a another mechanism to load
commands using the main class. To do this simply specify a list of fully qualified name commands, e.g:
Given a module ``foo`` with a command ``bar``:

.. code:: python

    from clinner.run.main import Main


    class FooMain(Main):
        commands = (
            'foo.bar',
        )

This bar command will be assigned as a ``staticmethod`` to FooMain class to provide an easy access: ``FooMain.bar()``.

In case of overriding a command already imported, the one defined in the class will prevail, e.g:

.. code:: python

    from clinner.run.main import Main


    class FooMain(Main):
        commands = (
            'foo.bar',
        )

        @staticmethod
        @command
        def bar(*args, **kwargs):
            pass  # This command will be the executed instead of foo.bar

Mixins
======

Clinner provides some useful mixins for main classes that adds different behaviors to these classes.

.. automodule:: clinner.run.mixins.health_check
    :members:
