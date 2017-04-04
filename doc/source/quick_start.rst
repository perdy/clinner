Quick Start
***********

1. Install this package using pip:

.. code-block:: bash

    pip install clinner

2. Create a command

.. code-block:: python

    from clinner.command import command

    @command
    def foo(*args, **kwargs):
        return True

3. Create a main file:

.. code-block:: python

    from clinner.run.main import Main

    if __name__ == '__main__':
        sys.exit(Main().run())
