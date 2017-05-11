Django Commands
***************

Using previously defined Main classes it's possible to wrap it as a Django command:

.. code:: python

    from clinner.run.main import Main


    class FooMain(Main):
        description = 'Foo main'

        commands = (
            'foo.bar',
        )

    class FooDjangoCommand(DjangoCommand):
        main_class = FooMain

This class handles the django commands arguments as well as passing them to run method.

.. autoclass:: clinner.run.django_command.DjangoCommand
    :members:

