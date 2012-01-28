#!/usr/bin/env python
# Mr. Repo - A very simple repo manager of repos.
# Author: Ryan McGowan
version = "0.1.0"

from argparse import ArgumentParser, SUPPRESS, RawDescriptionHelpFormatter
from textwrap import dedent
from yaml import load


class MrRepo(object):
    """
    The MrRepo class used to do all of the dirty work behind MrRepo.

    This class contains the basic functionality of the Mr. Repo project
    including the argument parser, and `.mr_repo.yml` and `.this_repo`
    management.
    """

    def __init__(self, prog='mr_repo', args=None, execute=False,
            config_file=".mr_repo.yml", repo_file='.this_repo'):
        self.version = version
        self.parser = ArgumentParser(
                prog=prog,
                formatter_class=RawDescriptionHelpFormatter,
                conflict_handler='resolve',
                description='Mr. Repo is a very simple repo manager of repos.',
                epilog='See the README (https://github.com/RyanMcG/Mr-Repo)' \
                        'for more information.'
                        )
        self._command_term = 'command'
        self.__setup_parser()
        self._config_file_name = config_file
        self._repo_file_name = repo_file

        # Run parse_args on passed in args if available
        if isinstance(args, list):
            self.parse_args(args)
        # Optionally execute the sub-command automatically
        if execute:
            self.execute()

    def _read_config_files(self):
        """Read `.mr_repo.yml` and `.this_repo` files to determine state the of
        the repository."""
        config = load(self._config_file_name)
        self.repos = config['repos']
        # TODO: Fill this out

    def __setup_parser(self):
        self.parser.add_argument('--version', action='version',
                version="Mr. Repo " + self.version)
        subparsers = self.parser.add_subparsers(
                title='Commands',
                description='Valid Mr. Repo commands:',
                dest=self._command_term,
                help='The user must use one of these commands (otherwise ' \
                        'they can use the help and version flags).')

        #Parsing for `init` command
        init_parser = subparsers.add_parser('init',
                formatter_class=RawDescriptionHelpFormatter,
                description=dedent(self.init_command.__doc__))
        init_parser.add_argument('--clean', '-c', dest='clean',
                action='store_true', default=False, help='ignore current ' \
                        'state of directory being initiliazed as a repo and ' \
                        'create a blank repo')
        init_parser.set_defaults(func=self.init_command)

        #Parsing for `list` command
        list_parser = subparsers.add_parser('list',
                formatter_class=RawDescriptionHelpFormatter,
                description=dedent(self.list_command.__doc__))
        mutex_list_args = list_parser.add_mutually_exclusive_group()
        # --not-available Just show currently unavailable repos
        mutex_list_args.add_argument('--not-available', '-n',
                dest='unavailable', action='store_true', default=SUPPRESS,
                help='list only currently unavailable repos.')
        # --all to show all repos (currently available or not)
        mutex_list_args.add_argument('--all', '-a', dest='all',
                action='store_true', default=SUPPRESS, help='list all repos' \
                        '(i.e. currently available or not)')

        list_parser.set_defaults(func=self.list_command)

        # Parser for `add` command
        add_parser = subparsers.add_parser('add',
                description=dedent(self.add_command.__doc__))
        add_parser.set_defaults(func=self.add_command)
        # Parser for `rm` command
        rm_parser = subparsers.add_parser('rm',
                description=dedent(self.rm_command.__doc__))
        rm_parser.set_defaults(func=self.rm_command)
        # Parser for `get` command
        get_parser = subparsers.add_parser('get',
                description=dedent(self.get_command.__doc__))
        get_parser.set_defaults(func=self.get_command)

        # Parser for `unget` command
        unget_parser = subparsers.add_parser('unget',
                description=dedent(self.unget_command.__doc__))
        unget_parser.add_argument('--force', '-f', dest='force',
                action='store_true', default=False, help='Force removal of' \
                        'repository even if it contains uncommitted changes.')
        unget_parser.set_defaults(func=self.unget_command)

    def parse_args(self, args):
        self.args = self.parser.parse_args(args)

    def print_help(self):
        self.parser.print_help()

    def execute(self):
        if callable(self.args.func):
            self.args.func()
        else:
            print("INTERNAL ERROR: Couldn't parse arguments!")
            self.print_help()

    # Mr. Repo Commands

    def init_command(self):
        """
        Initialize a new Mr. Repo controlled repository.

        By default Mr. Repo scans the directory being initialized for existing
        repositories and adds them to the tracking files.  This feature can be
        overridden with the `--clean` option.'
        """
        print(self.args.command)

    def add_command(self):
        """Add a definition of a local repository to the Mr. Repo
        repository."""
        print(self.args.command)

    def rm_command(self):
        """Remove a definition of a local repository from the Mr. Repo
        repository."""
        print(self.args.command)

    def list_command(self):
        """
        List Mr. Repo repositories.

        Lists Mr. Repo repositories that are currently available by default.
        Command line flags ([-a | -all] or [-n | --not-available]) may be used
        to specify which Mr. Repo repositories are listed.
        """
        print(self.args.command)

    def get_command(self):
        """Get a repository from the defined in the Mr. Repo repository."""
        print(self.args.command)

    def unget_command(self):
        """Remove a repository defined in the Mr. Repo repository from the
        local system."""
        print(self.args.command)

    def update_command(self):
        """Interprets Mr. Repo controlled directory and automatically updates
        tracking files based on its findings."""
        print(self.args.command)

if __name__ == '__main__':
    from sys import argv
    import re
    prog = "mr_repo"
    if (len(argv) > 0):
        prog = argv.pop(0)
        # If prog does not look something like Mr. Repo then change it
        if None == re.search('mr(\.|)([-_ ]{0,2})repo', prog,
                flags=re.IGNORECASE):
            prog = "mr_repo"
    #Create an instance of MrRepo
    repomr = MrRepo(prog=prog, args=argv, execute=True)
