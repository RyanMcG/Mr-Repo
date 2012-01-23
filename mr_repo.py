#!/usr/bin/env python
# Mr. Repo - A very simple repo manager of repos.
# Author: Ryan McGowan
version = "0.1.0"

from argparse import ArgumentParser, SUPPRESS


class MrRepo(object):
    """
    The MrRepo class used to do all of the dirty work behind MrRepo.

    This class contains the basica functionality of the Mr. Repo project
    including the argument parser, and `.mr_repo.yml` and `.this_repo`
    management.
    """

    def __init__(self, prog='mr_repo'):
        self.version = version
        self.parser = ArgumentParser(
                prog=prog,
                description='Mr. Repo is a very simple repo manager of repos.',
                epilog='See the README (https://github.com/RyanMcG/Mr-Repo)'\
                        'for more information.',
                conflict_handler='resolve'
                )
        self.__setup_parser()

    def __setup_parser(self):
        self.parser.add_argument('--version', action='version',
                version="Mr. Repo " + self.version)
        subparsers = self.parser.add_subparsers(
                title='Commands',
                description='Valid Mr. Repo commands:',
                help='The user must use one of these commands (otherwise they'\
                        'can use the help and version flags).')

        #Parsing for `init` command
        init_parser = subparsers.add_parser('init')
        clean_args = init_parser.add_mutually_exclusive_group()
        clean_args.add_argument("-c", dest='clean', action='store_true',
                default=False)
        clean_args.add_argument("--clean", dest='clean', action='store_true',
                default=False)

        #Parsing for `list` command
        list_parser = subparsers.add_parser('list')
        mutex_list_args = list_parser.add_mutually_exclusive_group()

        # --not-available Just show currently unavailable repos
        unavail_args = mutex_list_args.add_mutually_exclusive_group()
        all_args = mutex_list_args.add_mutually_exclusive_group()
        unavail_args.add_argument('-n', dest='unavailable',
                action='store_true', default=SUPPRESS)
        unavail_args.add_argument('--not-available', dest='unavailable',
                action='store_true', default=SUPPRESS)
        # --all to show all repos (currently availabel or not)
        all_args.add_argument('-a', dest='all', action='store_true',
                default=SUPPRESS)
        all_args.add_argument('--all', dest='all', action='store_true',
                default=SUPPRESS)

        # Parser for `add` command
        subparsers.add_parser('add')
        # Parser for `rm` command
        subparsers.add_parser('rm')
        # Parser for `get` command
        subparsers.add_parser('get')

        # Parser for `unget` command
        unget_parser = subparsers.add_parser('unget')
        unget_args = unget_parser.add_mutually_exclusive_group()
        unget_args.add_argument('-f', dest='force', action='store_true',
                default=False)
        unget_args.add_argument('--force', dest='force', action='store_true',
                default=False)

    def parse_args(self, args):
        self.args = self.parser.parse_args(args)

    def print_help(self):
        self.parser.print_help()

if __name__ == '__main__':
    from sys import argv
    prog = "mr_repo"
    if (len(argv) > 0):
        prog = argv.pop(0)
    #print(str(argv))
    repomr = MrRepo(prog=prog)
    repomr.parse_args(argv)
