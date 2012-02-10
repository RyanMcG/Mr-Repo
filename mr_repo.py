"""Mr. Repo - A very simple reposoitory for managing other repositories."""
# Author: Ryan McGowan
version = "0.2.1"

from argparse import (ArgumentParser, SUPPRESS, RawDescriptionHelpFormatter,
        Action, ArgumentTypeError)
from textwrap import dedent
from os import path
import git
import shutil
import yaml


class MrRepoDirAction(Action):
    """Action to be called on dir arg for mr repo."""

    @classmethod
    def check_dir(this, adir, config_file_name, is_init):
        apath = path.abspath(path.normpath(adir))
        if not path.isdir(apath):
            raise ArgumentTypeError("ERROR: %s is not a directory." % apath)

        if not is_init:
            if not path.isfile(path.join(apath, config_file_name)):
                raise ArgumentTypeError("ERROR: %s is not a Mr. Repo repo." %
                        apath)
        return apath

    def __call__(self, parser, namespace, values, option_string=None):
        apath = MrRepoDirAction.check_dir(values, parser._config_file_name,
                namespace.command == 'init')

        setattr(namespace, self.dest, apath)


class MrRepo(object):
    """
    The MrRepo class used to do all of the dirty work behind MrRepo.

    This class contains the basic functionality of the Mr. Repo project
    including the argument parser, and `.mr_repo.yml` and `.this_repo`
    management.
    """

    def __init__(self, prog='mr_repo', args=None, execute=False, quiet=False,
            config_file=".mr_repo.yml", repo_file='.this_repo', one_use=False):
        self.version = version
        self.config = {'repos': {}}
        self.repos = []
        self._command_term = 'command'
        self._config_file_name = config_file
        self._repo_file_name = repo_file

        #Setup parser
        self.parser = ArgumentParser(
                prog=prog,
                formatter_class=RawDescriptionHelpFormatter,
                conflict_handler='resolve',
                description='Mr. Repo is a very simple repo manager of repos.',
                epilog='See the README (https://github.com/RyanMcG/Mr-Repo) ' \
                        'for more information.')
        self.__setup_parser()

        # Run parse_args on passed in args if available
        if isinstance(args, list):
            self.parse_args(args)

            # Read config
            self.setup_files()
            if not self.is_init:
                self.read_config()

        # Optionally execute the sub-command automatically
        if execute:
            result = self.execute()
            if isinstance(result, str) and not quiet:
                print(result)

        if one_use:
            self.close()

    # Private functions

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
                        'state of directory being initialized as a repo and ' \
                        'create a blank repo')
        init_parser.set_defaults(func=self.init_command)

        #Parsing for `list` command
        list_parser = subparsers.add_parser('list',
                formatter_class=RawDescriptionHelpFormatter,
                description=dedent(self.list_command.__doc__))
        mutex_list_args = list_parser.add_mutually_exclusive_group()
        # --unavailable Just show currently unavailable repos
        mutex_list_args.add_argument('--unavailable', '-u',
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
        add_parser.add_argument('path', help='Path to the repository being ' \
                'put under Mr. Repo control', type=self.__path)
        add_parser.set_defaults(func=self.add_command)
        # Parser for `rm` command
        rm_parser = subparsers.add_parser('rm',
                description=dedent(self.rm_command.__doc__))
        rm_parser.add_argument('name', help='Name of the repository being ' \
                'removed from Mr. Repo control')
        rm_parser.set_defaults(func=self.rm_command)
        # Parser for `get` command
        get_parser = subparsers.add_parser('get',
                description=dedent(self.get_command.__doc__))
        get_parser.add_argument('name', help='Name of the repository being ' \
                'pulled into the local  Mr. Repo repo')
        get_parser.set_defaults(func=self.get_command)

        # Parser for `unget` command
        unget_parser = subparsers.add_parser('unget',
                description=dedent(self.unget_command.__doc__))
        unget_parser.add_argument('--force', '-f', dest='force',
                action='store_true', default=False, help='Force removal of ' \
                        'repository even if it contains uncommitted changes.')
        unget_parser.add_argument('name', help='Name of the repository ' \
                'being removed from the local Mr. Repo repo')
        unget_parser.set_defaults(func=self.unget_command)

        for sp in subparsers.choices.values():
            sp._config_file_name = self._config_file_name
            sp.add_argument('--dir', '-d', dest="dir", default='.',
                    help='The Mr. Repo directory being worked on.',
                    action=MrRepoDirAction)

    def __path(self, spath):
        extra = " so it cannot be added to Mr. Repo."
        try:
            apath = path.abspath(path.normpath(spath))
            if not path.isdir(apath):
                raise ArgumentTypeError("%s is not a directory" % spath +
                        extra)
            if self._get_repo(apath) == None:
                raise ArgumentTypeError("%s is not valid repository" % spath +
                        extra)
        except Exception as inst:
            print("ERROR: " + inst.message)

        return apath

    def __repo(self, repo_str):
        """Function returns true if repo_str is a Mr. Repo controlled repo."""
        return repo_str in self.config.get('repos').keys()

    # Pseudo private functions

    def _get_repo(self, apath):
        try:
            repo = git.Repo(apath)
        except:
            return None
        return repo

    # Public functions

    def setup_files(self):
        self.config_path = path.join(self.args.dir, self._config_file_name)
        self.repo_file_path = path.join(self.args.dir, self._repo_file_name)
        if not path.isfile(self.config_path):
            self.config_file = file(self.config_path, 'w')
        self.config_file = file(self.config_path, 'r+')
        if not path.isfile(self.repo_file_path):
            self.repo_file = file(self.repo_file_path, 'w')
        self.repo_file = file(self.repo_file_path, 'r+')

    def read_config(self):
        """Read `.mr_repo.yml` and `.this_repo` files to determine state the of
        the repository."""
        self.config_file.seek(0)
        self.config = yaml.load(self.config_file)
        self.repo_file.seek(0)
        self.repos = filter(self.__repo, [repo.rstrip() for repo in
            self.repo_file.readlines()])

    def write_config(self):
        """Write config to config file."""
        # Delete contents of files
        self.config_file.seek(0)
        self.config_file.truncate()
        self.repo_file.seek(0)
        self.repo_file.truncate()

        # Write contents to files
        yaml.dump(self.config, self.config_file)
        self.repo_file.write('\n'.join(self.repos))
        if len(self.repos) > 0:
            self.repo_file.write('\n')

    def parse_args(self, args):
        try:
            self.args = self.parser.parse_args(args)
            self.is_init = self.args.command == 'init'
            if self.args.dir == '.':
                self.args.dir = MrRepoDirAction.check_dir(self.args.dir,
                        self._config_file_name, self.is_init)
        except ArgumentTypeError as inst:
            print(inst.message)
            self.print_help()
            exit(2)

    def print_help(self):
        self.parser.print_help()

    def execute(self):
        if callable(self.args.func):
            result = self.args.func()
        else:
            print("INTERNAL ERROR: Couldn't parse arguments!")
            self.print_help()
        return result

    def close(self):
        """Close the config files."""
        if hasattr(self, 'config_file') and isinstance(self.config_file,
                file):
            self.config_file.close()
        if hasattr(self, 'repo_file') and isinstance(self.repo_file, file):
            self.repo_file.close()

    # Mr. Repo Commands

    def init_command(self):
        """
        Initialize a new Mr. Repo controlled repository.

        By default Mr. Repo scans the directory being initialized for existing
        repositories and adds them to the tracking files.  This feature can be
        overridden with the `--clean` option.'
        """
        if not self.args.clean:
            self.update_command()
        self.write_config()
        return "Successfully initialized Mr. Repo at '%s'." % self.args.dir

    def add_command(self):
        """Add a definition of a local repository to the Mr. Repo
        repository."""
        repo_name = path.basename(self.args.path)
        if not self.__repo(repo_name):
            rep = self._get_repo(self.args.path)
            if rep != None:
                self.repos.append(path.basename(self.args.path))
                if len(rep.remotes) > 0:
                    repo_dict = {repo_name: {'type': 'Git',
                        'remote': rep.remote().url}}
                else:
                    repo_dict = {repo_name: {'type': 'Git'}}
                self.config.get('repos').update(repo_dict)
                self.write_config()
                result = "Successfully added '%s' to Mr. Repo." % repo_name
            else:
                result = "ERROR: %s is not a not a supported repository." % \
                        self.args.path
        else:
            result = ("ERROR: %s already in %s (i.e. controlled by Mr. "
                    "Repo).") % (repo_name, self._config_file_name)
        return result

    def rm_command(self):
        """Remove a definition of a local repository from the Mr. Repo
        repository. Nothing is removed from the filesystem (use `unget` for
        that."""
        name = self.args.name

        if name in self.config['repos'].keys():
            self.config['repos'].pop(name)
            if name in self.repos:
                self.repos.remove(name)
            ret = "Successfully remove '%s' from Mr. Repo control."
            self.write_config()
        else:
            ret = "ERROR: '%s' is not a Mr. Repo controlled repository." % name

        return ret

    def list_command(self):
        """
        List Mr. Repo repositories.

        Lists Mr. Repo repositories that are currently available by default.
        Command line flags ([-a | -all] or [-u | --unavailable]) may be used
        to specify which Mr. Repo repositories are listed.
        """
        repos = self.config['repos']

        # Filter down all repos if we do not have the all flag or were given
        # the unavailable flag.
        if hasattr(self.args, 'unavailable') and self.args.unavailable:
            # Unavailable means it is in the config, but not in self.repos.
            repos = dict(filter(lambda x: x[0] not in self.repos,
                repos.items()))
        elif not (hasattr(self.args, 'all') and self.args.all):
            # The default, filter so that only available repos get through
            repos = dict(filter(lambda x: x[0] in self.repos, repos.items()))

        max_repo_length = 0
        for key in repos.keys():
            new_len = len(key)
            if new_len > max_repo_length:
                max_repo_length = new_len

        return '\n'.join([str(key.ljust(max_repo_length) + " - [" +
            item['type'] + "] remote: " + item['remote']) for key, item in
            repos.items()])

    def get_command(self):
        """Get a repository defined in the Mr. Repo repository, but not
        available locally."""
        name = self.args.name

        if name in self.config['repos'].keys():
            remote = self.config['repos'][name]['remote']
            repo_type = self.config['repos'][name]['type']
            if repo_type == "Git":
                new_repo = git.Repo.clone_from(remote,
                        path.join(self.args.dir, name))
                self.repos.append(name)
                ret = "Successfully cloned '%s' into '%s'." % (name,
                    new_repo.working_dir)
                self.write_config()
            else:
                ret = "ERROR: Repositories of type '%s' are not supported " % \
                        repo_type
        else:
            ret = "ERROR: '%s' is not a Mr. Repo controlled repository." % name

        return ret

    def unget_command(self):
        """Remove a repository defined in the Mr. Repo repository from the
        local system."""
        name = self.args.name

        if name in self.config['repos'].keys() and name in self.repos:
            repo_path = path.join(self.args.dir, name)
            repo_type = self.config['repos'][name]['type']
            ret = "Successfully removed the local copy of '%s'." % name
            # Check that it is a Git repo
            if repo_type == 'Git':
                repo = git.Repo(repo_path)
                # If we aren't forcing removal make sure it isn't dirty
                if not (hasattr(self.args, 'force') and self.args.force) and \
                        repo.is_dirty():
                    ret = "ERROR: '%s' is dirty. Fix it or use the " \
                            "`--force` option to force it's removal." % name
                else:
                    # Everything is ok. So we now do the removing
                    shutil.rmtree(repo_path)
                    self.repos.remove(name)
            else:
                ret = "ERROR: Repositories of type '%s' are not supported " % \
                        repo_type
        else:
            ret = "ERROR: '%s' is not a currently checked out Mr. Repo " \
                    "controlled repository." % name
        return ret

    def update_command(self):
        """Interprets Mr. Repo controlled directory and automatically updates
        tracking files based on its findings."""
        pass
