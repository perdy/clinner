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

Builder Main
============
Example of main module with build utilities such as unit tests, lint, sphinx doc, tox and dist packaging:

.. code-block:: python

    #!/usr/bin/env python
    import sys

    from clinner.run import Main


    class Build(Main):
        commands = (
            'clinner.run.commands.pytest.pytest',
            'clinner.run.commands.prospector.prospector',
            'clinner.run.commands.sphinx.sphinx',
            'clinner.run.commands.tox.tox',
            'clinner.run.commands.dist.dist',
        )


    if __name__ == '__main__':
        sys.exit(Build().run())

Django Main
===========
Example of main module for a Django application that uses uwsgi, health-check, prospector, pytest.

.. code-block:: python

    #!/usr/bin/env python3.6
    """Run script.
    """
    import argparse
    import multiprocessing
    import os
    import shlex
    import sys
    from socket import gethostname
    from typing import List

    import hvac
    from clinner.command import Type as CommandType, command
    from clinner.run import HealthCheckMixin, Main as BaseMain
    from django.core.exceptions import ImproperlyConfigured

    PYTHON = 'python3.6'
    COVERAGE = 'coverage'
    PROSPECTOR = 'prospector'
    HEALTH_CHECK = 'health_check'

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


    @command(command_type=CommandType.SHELL)
    def migrate(*args, **kwargs) -> List[List[str]]:
        cmd = shlex.split(f'{PYTHON} manage.py migrate')
        cmd += args
        return [cmd]


    @command(command_type=CommandType.SHELL)
    def build(*args, **kwargs) -> List[List[str]]:
        return migrate('--fake-initial') + collectstatic('--noinput')


    @command(command_type=CommandType.SHELL)
    def manage(*args, **kwargs) -> List[List[str]]:
        cmd = shlex.split(f'{PYTHON} manage.py')
        cmd += args
        return [cmd]


    @command(command_type=CommandType.SHELL)
    def unit_tests(*args, **kwargs) -> List[List[str]]:
        parallel_count = multiprocessing.cpu_count()
        coverage_erase = shlex.split(f'{COVERAGE} erase')

        tests = shlex.split(f'{COVERAGE} run --concurrency=multiprocessing manage.py test --parallel {parallel_count}')
        tests += args

        coverage_combine = shlex.split(f'{COVERAGE} combine')
        coverage_report = shlex.split(f'{COVERAGE} report')
        coverage_xml = shlex.split(f'{COVERAGE} xml')
        coverage_html = shlex.split(f'{COVERAGE} html')

        return [coverage_erase, tests, coverage_combine, coverage_xml, coverage_html, coverage_report]


    @command(command_type=CommandType.SHELL)
    def prospector(*args, **kwargs) -> List[List[str]]:
        cmd = [PROSPECTOR]
        cmd += args
        return [cmd]


    @command(command_type=CommandType.SHELL)
    def runserver(*args, **kwargs) -> List[List[str]]:
        cmd = shlex.split(f'{PYTHON} manage.py runserver --nothreading')
        cmd += args
        return migrate('--fake-initial') + [cmd]


    @command(command_type=CommandType.SHELL)
    def uwsgi(*args, **kwargs) -> List[List[str]]:
        http = f':{os.environ["APP_PORT"]}'
        stats = f':{os.environ["STATS_PORT"]}'
        ini = 'uwsgi.ini'
        cmd = ['uwsgi', '--http', http, '--stats', stats, '--ini', ini]
        cmd += args
        return migrate('--fake-initial') + [cmd]


    @command(command_type=CommandType.SHELL)
    def collectstatic(*args, **kwargs) -> List[List[str]]:
        cmd = shlex.split(f'{PYTHON} manage.py collectstatic')
        cmd += args
        return [cmd]


    @command(command_type=CommandType.SHELL)
    def shell(*args, **kwargs) -> List[List[str]]:
        cmd = shlex.split(f'{PYTHON} manage.py shell')
        cmd += args
        return [cmd]


    @command(command_type=CommandType.SHELL)
    def health_check(*args, **kwargs) -> List[List[str]]:
        """
        Run health-check
        """
        cmd = [HEALTH_CHECK]
        cmd += args
        return [cmd]


    class Main(HealthCheckMixin, BaseMain):
        commands = (
            'migrate',
            'build',
            'manage',
            'unit_tests',
            'prospector',
            'runserver',
            'uwsgi',
            'collectstatic',
            'shell',
            'health_check',
        )

        def add_arguments(self, parser: argparse.ArgumentParser):
            parser.add_argument('-s', '--settings', default='Development', help='Settings module')

        def inject_app_settings(self):
            """
            Injecting own settings.
            """
            config_name = self.args.settings
            os.environ['APP_HOST'] = os.environ.get('HOSTNAME', os.environ.get('APP_HOST', '0.0.0.0'))
            os.environ['APP_PORT'] = os.environ.get('PORT_8000', os.environ.get('APP_PORT', '8000'))
            os.environ['STATS_PORT'] = os.environ.get('PORT_9000', os.environ.get('STATS_PORT', '9000'))

            # Django
            os.environ['DJANGO_SETTINGS_MODULE'] = 'your_app.settings'
            os.environ['DJANGO_CONFIGURATION'] = self.args.settings

            # Plugins
            os.environ['CLINNER_SETTINGS'] = self.args.settings or f'your_app.plugins_settings.clinner:{self.args.settings}'
            os.environ['HEALTH_CHECK_SETTINGS'] = f'your_app.plugins_settings.health_check:{self.args.settings}'

        def health_check(self):
            """
            Does a check using Health Check application.

            :return: 0 if healthy.
                """
                return not self.run_command('manage', 'health_check', 'health', '-e')


        if __name__ == '__main__':
            sys.exit(Main().run())
