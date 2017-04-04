"""
File used to check dynamic commands loading.
"""

from clinner.command import command


@command
def foobar(*args, **kwargs):
    kwargs['q'].put(42)

