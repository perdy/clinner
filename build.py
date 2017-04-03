#!/usr/bin/env python
import sys

from clinner.run.commands.nose import nose
from clinner.run.commands.prospector import prospector
from clinner.run.commands.sphinx import sphinx
from clinner.run.commands.tox import tox
from clinner.run.commands.dist import dist
from clinner.run import Main


def main():
    return Main().run()


if __name__ == '__main__':
    sys.exit(main())
