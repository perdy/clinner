Examples
********

Some Clinner examples.

Simple Main
===========
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
============
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
