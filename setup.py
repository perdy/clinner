# -*- coding: utf-8 -*-

import os
import re
import shutil
import sys

from setuptools import Command, setup

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

if sys.version_info[0] == 2:
    from codecs import open


def parse_requirements(requirements_file):
    with open(requirements_file) as f:
        return [l.strip().split(';')[0] for l in f if re.match(r'[a-zA-Z].*', l.strip())]


# Read requirements
_requirements_file = os.path.join(BASE_DIR, 'requirements.txt')
_REQUIRES = parse_requirements(_requirements_file)

# Read description
with open(os.path.join(BASE_DIR, 'README.rst'), encoding='utf-8') as f:
    _LONG_DESCRIPTION = f.read()

_CLASSIFIERS = (
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Natural Language :: English',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Topic :: Software Development :: Libraries :: Python Modules',
)

_KEYWORDS = ' '.join([
    'python',
    'command',
    'cli',
    'interface',
    'run',
    'script',
])

setup(
    name='clinner',
    version='1.9.2',
    description='Command Line Interface builder that helps creating an entry point for your application.',
    long_description=_LONG_DESCRIPTION,
    author='José Antonio Perdiguero López',
    author_email='perdy.hh@gmail.com',
    maintainer='José Antonio Perdiguero López',
    maintainer_email='perdy.hh@gmail.com',
    url='https://github.com/PeRDy/Clinner',
    download_url='https://github.com/PeRDy/Clinner',
    packages=[
        'clinner',
    ],
    include_package_data=True,
    install_requires=_REQUIRES,
    extras_require={
        'dev': [
            'setuptools',
            'pip',
            'wheel',
            'twine',
            'bumpversion',
            'pre-commit',
        ] + _TESTS_REQUIRES,
    },
    license='GPLv3',
    zip_safe=False,
    keywords=_KEYWORDS,
    classifiers=_CLASSIFIERS,
)
