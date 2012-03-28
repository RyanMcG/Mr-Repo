# Author: Ryan McGowan

from argparse import (ArgumentParser, RawDescriptionHelpFormatter, Action,
        ArgumentTypeError)
from textwrap import dedent
from mr_repo import version
import os
import shutil
import yaml
import git


class _MrRepoDirAction(Action):
    """Action to be called on dir arg for mr repo."""

    @classmethod
    def check_dir(this, adir, config_file_name, is_init):
        apath = os.path.normpath(adir)
        if not os.path.isdir(apath):
            raise ArgumentTypeError("ERROR: %s is not a directory." % apath)

        if not is_init:
            if not os.path.isfile(os.path.join(apath, config_file_name)):
                raise ArgumentTypeError("ERROR: %s is not a Mr. Repo repo." %
                        apath)
        return apath

    def __call__(self, parser, namespace, values, option_string=None):
        apath = _MrRepoDirAction.check_dir(values, parser._config_file_name,
                namespace.command == 'init')

        setattr(namespace, self.dest, apath)


class Repossesser(object):
    """
    The Repossesser class used to do all of the dirty work behind Mr. Repo.

    This class contains the basic functionality of the Mr. Repo project
    including the argument parser, and `.mr_repo.yml` and `.this_repo`
    management.
    """

    def __init__(self, prog='mr_repo', args=None, execute=False, quiet=False,
            config_file=".mr_repo.yml", repo_file='.this_repo', one_use=False,
            verbose=False):
        self.config = {'repos': {}}
        self.repos = []
        self._command_term = 'command'
        self._config_file_name = config_file
        self._repo_file_name = repo_file
        self.verbose = verbose

        # Setup parser
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
                version="Mr. Repo " + version)

        self.parser._config_file_name = self._config_file_name
        self.parser.add_argument('--verbose', '-v', dest="verbose",
                default=False,
                help='Run this command verbosely to show debug output.',
                action='store_true')
        self.parser.add_argument('--dir', '-d', dest="dir", default='.',
                help='The Mr. Repo directory being worked on.',
                action=_MrRepoDirAction)
        subparsers = self.parser.add_subparsers(
                title='Commands',
                description='Valid Mr. Repo commands:',
                dest=self._command_term,
                help='The user must use one of these commands (otherwise ' \
                        'they can use the help and version flags).')

        # Parsing for `init` command
        init_parser = subparsers.add_parser('init',
                formatter_class=RawDescriptionHelpFormatter,
                description=dedent(self.init_command.__doc__))
        init_parser.add_argument('--clean', '-c', dest='clean',
                action='store_true', default=False, help='ignore current ' \
                        'state of directory being initialized as a repo and ' \
                        'create a blank repo')
        init_parser.set_defaults(func=self.init_command)

        # Parsing for `list` command
        list_parser = subparsers.add_parser('list',
                formatter_class=RawDescriptionHelpFormatter,
                description=dedent(self.list_command.__doc__))
        mutex_list_args = list_parser.add_mutually_exclusive_group()
        # --unavailable Just show currently unavailable repos
        mutex_list_args.add_argument('--unavailable', '-u',
                dest='unavailable', action='store_true', default=False,
                help='list only currently unavailable repos.')
        # --all to show all repos (currently available or not)
        mutex_list_args.add_argument('--all', '-a', dest='all',
                action='store_true', default=False, help='list all repos' \
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

        # Parser for `update` command
        update_parser = subparsers.add_parser('update',
                description=dedent(self.update_command.__doc__))
        update_parser.add_argument('--current-only', '-c',
                dest='local', action='store_true', default=False,
                help='Forces an update of configuration for local, ' \
                        'controlled repositories.')
        # --all to show all repos (currently available or not)
        update_parser.set_defaults(func=self.update_command)

        for sp in subparsers.choices.values():
            sp._config_file_name = self._config_file_name
            sp.add_argument('--dir', '-d', dest="dir", default='.',
                    help='The Mr. Repo directory being worked on.',
                    action=_MrRepoDirAction)
            sp.add_argument('--verbose', '-v', dest="verbose", default=False,
                    help='Run this command verbosely to show debug output.',
                    action='store_true')

    def __path(self, spath):
        extra = " so it cannot be added to Mr. Repo."
        apath = os.path.normpath(spath)
        if not os.path.isdir(apath):
            raise ArgumentTypeError("%s is not a directory" % spath +
                    extra)
        if self._get_repo(apath) == None:
            raise ArgumentTypeError("%s is not a valid repository" % spath +
                    extra)
        return apath

    # Pseudo private functions

    def _debug(self, debugging_info):
        if self.verbose:
            print("DEBUG: " + str(debugging_info))

    @classmethod
    def _get_repo(cls, apath):
        try:
            repo = git.Repo(apath)
        except:
            return None
        return repo

    @classmethod
    def find_repos(cls, start_path, max_depth=4):
        found_repos = []
        if max_depth >= 0:
            (base_path, directories, filenames) = os.walk(start_path,
                    followlinks=True).next()
            for directory in directories:
                directory = os.path.join(start_path, directory)
                directory_repo = cls._get_repo(directory)
                if isinstance(directory_repo, git.Repo):
                    found_repos.append(os.path.normpath(directory))
                else:
                    found_repos.extend(cls.find_repos(directory,
                        max_depth - 1))
        return found_repos

    # Public functions

    def check_repo_name(self, name):
        repo_name = os.path.basename(os.path.normpath(name))
        if self.is_conrtolled_repo(repo_name):
            return repo_name
        else:
            return False

    def setup_files(self):
        temp_config_path = os.path.join(self.args.dir, self._config_file_name)
        temp_repo_file_path = os.path.join(self.args.dir, self._repo_file_name)

        # If the config files do not exist, create them
        if not os.path.isfile(temp_config_path):
            open(temp_config_path, 'w')
        if not os.path.isfile(temp_repo_file_path):
            open(temp_repo_file_path, 'w')

        # Follow the link if it exists
        self.config_path = temp_config_path if \
                (not os.path.islink(temp_config_path)) else \
                os.readlink(temp_config_path)
        self.repo_file_path = temp_repo_file_path if \
                (not os.path.islink(temp_repo_file_path)) else \
                os.readlink(temp_repo_file_path)

        self.config_file = open(self.config_path, 'r+')
        self.repo_file = open(self.repo_file_path, 'r+')

    def read_config(self, check=True):
        """Read `.mr_repo.yml` and `.this_repo` files to determine state the of
        the repository."""
        self.config_file.seek(0)
        self.config = yaml.load(self.config_file)
        self.repo_file.seek(0)
        self.repos = filter(self.is_conrtolled_repo, [repo.rstrip() for repo in
            self.repo_file.readlines()])
        if check:
            self.check_config()

    def check_config(self, reread=False, compare_to_directory=True):
        """Checks to see whether config and repos are of the proper format.
        Optionally, this function can check values in config and repos against
        the Mr. Repo controlled directory."""
        if reread:
            self.read_config()

        #Check that self.repos is a list of strings
        repos_ok = isinstance(self.repos, list) and len(filter(lambda x: not \
                isinstance(x, str), self.repos)) == 0

        #Check to make sure that each entry in config has valid keys/values
        config_ok = isinstance(self.config, dict)
        if config_ok:
            try:
                config_ok = filter(lambda x: isinstance(x[0], str) and
                        isinstance(x[1], dict), self.config)
            except:
                config_ok = False

        return {'repos': repos_ok, 'config': config_ok}

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
            if hasattr(self.args, 'verbose'):
                self.verbose = self.verbose or self.args.verbose
            if self.args.dir == '.':
                self.args.dir = _MrRepoDirAction.check_dir(self.args.dir,
                        self._config_file_name, self.is_init)
        except ArgumentTypeError as inst:
            print(inst.message)
            print(str(self.args))
            exit(2)

    def is_conrtolled_repo(self, repo_str):
        """Function returns true if repo_str is a Mr. Repo controlled repo."""
        return repo_str in self.config.get('repos').keys()

    def execute(self):
        if callable(self.args.func):
            result = self.args.func()
        else:
            print("INTERNAL ERROR: Couldn't parse arguments!")
            self.parser.print_help()
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

    def add_command(self, path=None):
        """Add a definition of a local repository to the Mr. Repo
        repository."""
        # Path relative to CWD
        cur_rel_path = os.path.normpath(path or self.args.path)
        # Path relative to Mr. Repo directory
        mr_rel_path = os.path.relpath(cur_rel_path, self.args.dir)

        repo_name = os.path.basename(mr_rel_path)

        if not self.is_conrtolled_repo(repo_name):
            rep = self._get_repo(cur_rel_path)
            if rep != None:
                self.repos.append(os.path.basename(repo_name))
                if len(rep.remotes) > 0:
                    repo_dict = {repo_name: {'type': 'Git',
                        'remote': rep.remote().url, 'path': mr_rel_path}}
                else:
                    repo_dict = {repo_name: {'type': 'Git', 'path': mr_rel_path}}
                self._debug("Adding to config: " + str(repo_dict))
                self.config.get('repos').update(repo_dict)
                self.write_config()
                result = "Successfully added '%s' to Mr. Repo." % repo_name
            else:
                result = "ERROR: %s is not a supported repository." % \
                        cur_rel_path
        else:
            result = ("ERROR: %s is already controlled by Mr. Repo (i.e "
                    "it is in %s).") % (repo_name, self._config_file_name)
        return result

    def rm_command(self):
        """Remove a definition of a local repository from the Mr. Repo
        repository. Nothing is removed from the filesystem (use `unget` for
        that."""
        name = self.check_repo_name(self.args.name)

        if name:
            self.config['repos'].pop(name)
            if name in self.repos:
                self.repos.remove(name)
            ret = "Successfully removed '%s' from Mr. Repo control." % name
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

        return '\n'.join([str(key.ljust(max_repo_length) + " - [%s] %s" % \
                (item['type'], ', '.join(["%s: %s" % (name, value) for name,
                    value in filter(lambda x: x[0] != 'type', item.items())])))
                for key, item in repos.items()])

    def get_command(self):
        """Get a repository defined in the Mr. Repo repository, but not
        available locally."""
        name = self.check_repo_name(self.args.name)

        if name:
            if 'remote' in self.config['repos'][name]:
                remote = self.config['repos'][name]['remote']
                repo_type = self.config['repos'][name]['type']
                repo_path = os.relpath(os.path.join(self.args.dir,
                        self.config['repos'][name]['path'] or name))
                if repo_type == "Git":
                    new_repo = git.Repo.clone_from(remote, repo_path)
                    self.repos.append(name)
                    ret = "Successfully cloned '%s' into '%s'." % (name,
                        new_repo.working_dir)
                    self.write_config()
                else:
                    ret = "ERROR: Repositories of type '%s' are not " % \
                            repo_type + "supported"
            else:
                ret = "ERROR: %s does not have an associated " % name + \
                        "remote to repossess it from."
        else:
            ret = "ERROR: '%s' is not a Mr. Repo controlled repository." % name

        return ret

    def unget_command(self):
        """Remove a repository defined in the Mr. Repo repository from the
        local system."""
        name = self.check_repo_name(self.args.name)

        if name and name in self.repos:
            repo_path = os.path.relpath(os.path.join(self.args.dir,
                    self.config['repos'][name]['path'] or name))
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
        start_len = len(self.repos)
        repos = filter(lambda x: not self.is_conrtolled_repo(x),
                self.find_repos(self.args.dir if not hasattr(self.args, 'path')
                    else self.args.path))

        if hasattr(self.args, "current") and self.args.current:
            # Unavailable means it is in the config, but not in self.repos.
            repos = dict(filter(lambda x: x[0] in self.repos,
                repos.items()))

        # Add all of the repos
        map(self.add_command, repos)
        difference = len(self.repos) - start_len
        if difference > 0:
            success_str = "Successfully added %d new repositories." % \
                    difference
        elif difference < 0:
            success_str = "Successfully removed %d repositories." % \
                    difference
        else:
            success_str = "No updates made to controlled repos."
        return success_str
