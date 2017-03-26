#!/usr/bin/env python
import sys

from clinner.run.nose import Nose


def main():
    return Nose().run()


if __name__ == '__main__':
    sys.exit(main())
