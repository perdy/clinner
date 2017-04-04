import shlex

from clinner.command import Type, command

__all__ = ['sphinx']


@command(command_type=Type.SHELL,
         args=((('sphinx_command',), {'help': 'Sphinx command'}),
               (('--source',), {'help': 'Sources dir', 'default': 'doc/source'}),
               (('--build',), {'help': 'Build dir', 'default': 'doc/build'})),
         parser_opts={'help': 'Sphinx doc'})
def sphinx(*args, **kwargs):
    """
    Run an sphinx command.
    """
    return [shlex.split('sphinx-build -M %s %s %s' % (kwargs['sphinx_command'], kwargs['source'], kwargs['build']))]
