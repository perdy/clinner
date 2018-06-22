# Clinner
[![Build Status](https://travis-ci.org/PeRDy/clinner.svg?branch=master)](https://travis-ci.org/PeRDy/clinner)
[![codecov](https://codecov.io/gh/PeRDy/clinner/branch/master/graph/badge.svg)](https://codecov.io/gh/PeRDy/clinner)
[![PyPI version](https://badge.fury.io/py/clinner.svg)](https://badge.fury.io/py/clinner)

* **Version:** 1.11.1
* **Status:** Production/Stable
* **Author:** José Antonio Perdiguero López

Command Line Interface builder that helps creating an entry point for your application.

Check full [Clinner documentation].

## Quick start
Install this package using pip:

```bash
pip install clinner
```

Create a command

```python
from clinner.command import command

@command
def foo(*args, **kwargs):
    return True
```

Create a main file:

```python
from clinner.run.main import Main

if __name__ == '__main__':
    sys.exit(Main().run())
```

## Commands
Commands are declared using a decorator to register given functions. Commands are functions with the follow parameters:

1. `func`: Function that will be called when command would be executed.
2. `command_type`: Type of the command, could be a *bash* or *python* command.
3. `args`: Parser arguments for this command.
4. `parser_opts`: Command subparser's keywords, such as description.

This decorator allows to be used as a common decorator without arguments, where default type (*python*) will be used:

```python
@command
def foobar(bar):
    pass
```

Or specifying the type:

```python
@command(command_type=Type.PYTHON)
def foobar(bar):
    pass
```

But also is possible to provide command line arguments, as expected by argparse.ArgumentParser.add_argument:

```python
@command(args=((('-f', '--foo'), {'help': 'Foo argument that does nothing'}),                   # Command argument
               (('--bar',), {'action': 'store_true', 'help': 'Bar argument stored as True'})),  # Another argument
         parser_opts={'title': 'foobar_command', 'help': 'Help for foobar_command'})            # Parser parameters
def foobar(*args, **kwargs):
    pass
```

All commands will be registered in a command register that can be accessed through ``command.register``. Each entry in
this register is a dictionary with the fields declared at the beginning of this section.

## Main
A main class is defined to ease the creation of command line applications. This class follows the process:

1. Create a parser using ``argparse.ArgumentParser`` for the application:

    a) Calling all ``add_arguments(parser)`` methods from all super classes, e.g: ``clinner.mixins.HealthCheckMixin``.
    b) Addding a subparser for each command with their specific arguments.

2. Parse arguments using the argument parser created previously.

3. Inject variables into environment calling all super classes methods whose name starts with ``inject_``.

4. Load settings module from **CLINNER_SETTINGS** environment variable. More details below.


## Settings
Clinner settings can be specified through **CLINNER_SETTINGS** environment variable or using ``-s`` or ``--settings``
command line flags during invocation. The format to specify settings module or class should be either ``package.module``
or ``package.module:Class``.

### Default Arguments
Default arguments for commands. Let a command `foo` declared:

```python
default_args = {
    'foo': ['-v', '--bar', 'foobar'],
}
```

## Examples
Some Clinner examples.

### Simple Main
Example of a simple main with two defined commands `foo` and `bar`.

```python
#!/usr/bin/env python
import os
import shlex
import sys

from clinner.command import command, Type as CommandType
from clinner.run.main import Main


@command(command_type=CommandType.SHELL
         args=(('-i', '--input'),
               ('-o', '--output')),
         parser_opts={'help': 'Foo command'})
def foo(*args, **kwargs):
    """List of foo commands"""
    ls_cmd = shlex.split('ls')
    wc_cmd = shlex.split('wc')
    wc_cmd += [kwargs['input'], kwargs['output']]

    return [ls_cmd, wc_cmd]


@command(command_type=CommandType.PYTHON,
         parser_opts={'help': 'Bar command'})
def bar(*args, **kwargs):
    """Do a bar."""
    return True


if __name__ == '__main__':
    sys.exit(Main().run())
```

### Builder Main
Example of main module with build utilities such as unit tests, lint, sphinx doc, tox and dist packaging:

```python
#!/usr/bin/env python
import sys

from clinner.run import Main


class Build(Main):
    commands = (
        'clinner.run.commands.black.black',
        'clinner.run.commands.flake8.flake8',
        'clinner.run.commands.isort.isort',
        'clinner.run.commands.pytest.pytest',
        'clinner.run.commands.sphinx.sphinx',
        'clinner.run.commands.tox.tox',
    )


if __name__ == '__main__':
    sys.exit(Build().run())
```

Check [Clinner documentation] to see more advanced examples.

[Clinner documentation]: http://clinner.readthedocs.io
