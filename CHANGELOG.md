# Changes
v1.11.0 - 2018-06-22
 * Default logging level set as WARNING.
 * Return code logs level set as DEBUG.
 * DEBUG level shows commands list to be executed.
 * Command arguments log level set as DEBUG.

v1.10.0 - 2018-06-19
 * Use poetry for handling packaging and requirements.
 * Integrate black as code formatter.
 * Integrate flake8 as code linter.
 * Integrate isort as import formatter.
 * Replace tox previous tasks to use black, flake8 and isort.
 * New command for running black.
 * New command for running flake8.
 * New command for running isort.

v1.9.4 - 2018-04-24
 * Adds long description to setup.

v1.9.3 - 2018-04-17
 * Update setup.py to avoid dependencies and use Pipfile instead of requirements.txt

v1.9.2 - 2018-04-06
 * SIGINT handler for shell commands.

v1.9.1 - 2018-04-04
 * Compatible with Python 3.5

v1.9.0 - 2018-04-04
 * Refactor test to remove TestCase inheritance and use purely pytest.
 * Add inputs module with some functions for asking user data.

v1.8.2 - 2018-03-20
 * Run inject methods before getting clinner settings.

v1.8.1 - 2018-03-20
 * Inherit inject methods from Main parents.

v1.8.0 - 2018-03-19
 * Different verbose levels.

v1.2.0 - 2017-04-24
 * Added django commands wrapper for main classes.

v0.1.0 - 2017-02-27
 * Initial release.
