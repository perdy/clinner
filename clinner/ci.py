import argparse
import datetime
import io
import os
import re
import shlex
import subprocess
from configparser import ConfigParser

from colorama import Fore

from run_utils.cli import cli


class Main:
    def __init__(self):
        # Load args
        self.parser = argparse.ArgumentParser()
        self.add_arguments()
        self.args = self.parser.parse_args()

        # Load config
        self.config = ConfigParser()
        self.config.read('setup.cfg')

        # Attributes
        self.time = datetime.datetime.now()
        self.report_path = os.path.realpath(os.path.join('.', self.config['ci']['directory']))

        # Create report path
        if not os.path.exists(self.report_path):
            os.makedirs(self.report_path)

    def add_arguments(self):
        self.parser.add_argument('-d', '--detail', help='Show detailed info', action='store_true')
        self.parser.add_argument('-e', '--exit_on_fail', help='Exit on first failure', action='store_true')

    def _run_command(self, command, report=None):
        args = ['./run.py'] + shlex.split(command)
        if report:
            report_file_path = os.path.join(self.report_path, report)
            report_file = open(report_file_path, 'w')

        # Run command
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, bufsize=1)
        try:
            stdout = io.StringIO()

            for line in p.stdout:
                # Write to report file
                if report:
                    report_file.write(line)

                # Write to stdout if detailed mode
                if self.args.detail:
                    print(line, end='')

                # Write to text buffer
                stdout.write(line)
            p.wait()
        except KeyboardInterrupt:
            p.kill()
            return_code, stdout, stderr = -9, '', ''
        else:
            stdout.seek(0)
            return_code, stderr = p.returncode, p.stderr

        # Return code, stdout and stderr
        return return_code, stdout, stderr

    def run(self):
        error = 0

        # Run unit tests
        if not error:
            code, stdout, stderr = self._run_command('-s unit_tests unit_tests', report='unit_tests.txt')
            regex = re.compile(r'(\d+)%')
            try:
                coverage = int(regex.search(stdout.readlines()[-1]).group(1))
            except (IndexError, AttributeError):
                coverage = None
            formatted_coverage = '%d%%' % (coverage,) if coverage else 'NaN'
            result = Fore.RED + 'Fail' + Fore.RESET if code != 0 else Fore.GREEN + 'Success' + Fore.RESET
            cli.logger.info(Fore.RESET + '[1] Unit tests: %s. Coverage: %s.' % (result, formatted_coverage))
            error = error or code

        # Run prospector
        if not error:
            code, stdout, stderr = self._run_command('prospector --output-format grouped', report='prospector.txt')
            regex = re.compile(r'Messages Found: (\d+)')
            try:
                fails = int(regex.search(stdout.readlines()[-2]).group(1))
            except (IndexError, AttributeError):
                fails = None
            formatted_fails = str(fails) or 'NaN'
            result = Fore.RED + 'Fail' + Fore.RESET if code != 0 else Fore.GREEN + 'Success' + Fore.RESET
            cli.logger.info(Fore.RESET + '[2] Prospector: %s. Failures: %s.' % (result, formatted_fails))
            error = error or code

        return error
