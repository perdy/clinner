Example
=======

Full code example:

.. code-block:: python

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
