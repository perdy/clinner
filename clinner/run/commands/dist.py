import shlex

from clinner.command import Type, command

__all__ = ['dist']

VERSION_CHOICES = ('patch', 'minor', 'major')


@command(command_type=Type.SHELL_WITH_HELP,
         args=((('version',), {'help': 'Bump version', 'choices': VERSION_CHOICES}),),
         parser_opts={'help': 'Bump version, create package and upload it'})
def dist(*args, **kwargs):
    """
    Bump version, create package and upload it.
    """
    clean = shlex.split('rm -rf dist')
    bumpversion = shlex.split('bumpversion %s' % kwargs['version'])
    package = shlex.split('python setup.py sdist bdist_wheel')
    upload = shlex.split('twine upload dist/*')
    return [clean, bumpversion, package, upload]
