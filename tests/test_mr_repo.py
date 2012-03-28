"""DSL for Mr. Repo project.

Uses pea as a simple BDD framework around nose to make testing nicer. To run
the tests use nose (and rednose if you want nice color):

    nosetest --rednose -v
"""
# Author: Ryan McGowan

# Modify import path to import current code.
import sys
import os
sys.path.insert(0, os.path.abspath('..'))

from pea import step, TestCase, Given, When, Then, And, world
from mr_repo.repossesser import Repossesser
import git
import tempfile
import copy
import shutil

# Misc functions


def clone_state(mr_repo):
    """Clones the state of a Repossesser instance."""
    if isinstance(mr_repo, Repossesser):
        return {'config': copy.deepcopy(world.mr_repo.config),
                'repos': world.mr_repo.repos[:]}
    else:
        return None

# Given functions -------------------------------------------------------------


@step
def I_have_a_Mr_Repo_repository(execute=True, clean=False):
    """Creates a Mr. Repo repository and stores the inital state."""
    args = ['init', '-d', world.tdir]
    if clean:
        args.append('--clean')
    world.mr_repo = Repossesser(args=args, execute=execute, quiet=True)
    world.states = [clone_state(world.mr_repo)]


@step
def I_have_the_following_input(given_input):
    """Keep the given input for future use. This function can be called
    multiple times to emmulate multiple mr_repo commands."""
    if isinstance(given_input, str):
        if hasattr(world, 'given_input') and isinstance(world.given_input,
                list):
            world.given_input.append(given_input)
        else:
            world.given_input = [given_input]
    elif isinstance(given_input, list):
        world.given_input = given_input


@step
def I_have_a_git_repository_called(repo_name, bare=False):
    repo_dir = os.path.join(world.tdir, repo_name)
    world.repos.append(git.Repo.init(repo_dir, bare=bare))


@step
def I_have_a_nested_structure(levels, prefix='level_'):
    current_dir = world.tdir
    for level in range(levels):
        current_dir = os.path.join(current_dir, prefix + str(level + 1))
        if not os.path.isdir(current_dir):
            os.mkdir(current_dir)
    world.max_level = levels
    return os.path.normpath(current_dir)

# When functions --------------------------------------------------------------


@step
def I_parse_a_line_of_the_input():
    """Parse the given arguments."""
    args = world.given_input.pop(0).split()
    if '-d' not in args:
        args.extend(['-d', world.tdir])
    world.mr_repo.parse_args(args)


@step
def I_execute_the_command(close=True):
    """Run mr_repo.execute with the option of not closing the config files."""
    result = world.mr_repo.execute()
    if close:
        world.mr_repo.close()
    world.assertIsInstance(result, str)


@step
def I_execute_all_of_the_input():
    while len(world.given_input) > 0:
        I_parse_a_line_of_the_input()
        I_execute_the_command()
        I_setup_and_read_files()


@step
def I_execute_the_following_input(given_input):
    I_have_the_following_input(given_input)
    I_execute_all_of_the_input()


@step
def I_add_the_repository(repo_path):
    world.mr_repo.args.command = 'add'
    world.mr_repo.args.path = repo_path
    result = world.mr_repo.add_command()
    world.assertRegexpMatches(result, 'Success.*')


@step
def I_setup_and_read_files():
    """Setup config files for mr_repo instance."""
    world.mr_repo.setup_files()
    if not world.mr_repo.is_init:
        world.mr_repo.read_config()
    world.states.append(clone_state(world.mr_repo))

# Then functions --------------------------------------------------------------


@step
def I_have_a_clean_Mr_Repo_repository():
    world.assertDictEqual(world.states[len(world.states) - 1]['config'],
            {'repos': {}})
    world.assertListEqual(world.states[len(world.states) - 1]['repos'], [])


@step
def I_have_Mr_Repo_config_files():
    assert os.path.isfile(world.mr_repo.config_path)
    world.assertIsNotNone(world.mr_repo.config.get('repos'))
    assert os.path.isfile(world.mr_repo.repo_file_path)
    world.assertIsInstance(world.mr_repo.repos, list)


@step
def I_have_updated_config_files(config_check=world.assertNotEqual,
        repo_check=world.assertNotEqual):
    world.mr_repo.read_config()
    config_check(world.mr_repo.config, world.states[0]['config'])
    repo_check(world.mr_repo.repos, world.states[0]['repos'])

# Test cases ------------------------------------------------------------------


class RepossesserStories(TestCase):
    """Some test cases for Mr. Repo."""

    def setUp(self):
        """Setup RepossesserStories tests."""
        super(RepossesserStories, self).setUp()
        prefix = "tmpmrrepotesting"
        world.tdir = tempfile.mkdtemp(prefix=prefix)
        world.mr_repo = Repossesser()
        world.states = [clone_state(world.mr_repo)]
        world.repos = []

    def tearDown(self):
        super(RepossesserStories, self).tearDown()
        # Make sure the mr_repo files are closed
        if hasattr(world, 'mr_repo'):
            world.mr_repo.close()
            world.mr_repo = None

        # Make sure all the testing repos are gone
        for repo in world.repos:
            if isinstance(repo, git.Repo):
                # It is a Git repository
                if os.path.exists(repo.working_dir):
                    shutil.rmtree(repo.working_dir)

        # Make sure the test directory is gone
        if hasattr(world, 'tdir'):
            if os.path.exists(world.tdir):
                shutil.rmtree(world.tdir)

    @classmethod
    def __config_has_new_repo(cls, new_repo_name):
        def config_has_new_repo(new_config, old_config):
            """Test whether config has a new repository called %s.""" % \
                    new_repo_name
            world.assertIn(new_repo_name, new_config['repos'].keys())
            world.assertNotIn(new_repo_name, old_config['repos'].keys())
        return config_has_new_repo

    @classmethod
    def __repo_has_new_repo(cls, new_repo_name):
        def repos_has_new_repo(new_repos, old_repos):
            """Test whether repos has a new repository called %s.""" % \
                    new_repo_name
            world.assertIn(new_repo_name, new_repos)
            world.assertNotIn(new_repo_name, old_repos)
        return repos_has_new_repo

    # Stories -----------------------------------------------------------------

    def test_adding_a_git_repo(self):
        """Adding a valid directory/repo works."""
        repo_name = "Shoes"
        Given.I_have_a_git_repository_called(repo_name)
        And.I_have_a_Mr_Repo_repository(clean=True)
        When.I_add_the_repository(world.repos[0].working_dir)
        Then.I_have_updated_config_files(
                config_check=RepossesserStories.__config_has_new_repo(
                    repo_name),
                repo_check=RepossesserStories.__repo_has_new_repo(repo_name))

    def test_running_init_clean(self):
        """Running init with the '--clean' flag results in a clean repo."""
        Given.I_have_the_following_input('init --clean')
        When.I_parse_a_line_of_the_input()
        And.I_setup_and_read_files()
        And.I_execute_the_command()
        Then.I_have_a_clean_Mr_Repo_repository()

    def test_running_init_creates_files(self):
        """Running init results in correct config files."""
        Given.I_have_the_following_input('init')
        When.I_parse_a_line_of_the_input()
        And.I_setup_and_read_files()
        And.I_execute_the_command()
        Then.I_have_Mr_Repo_config_files()

    def test_update_searches_down_directories(self):
        repo_name = "Socks"
        current_dir = Given.I_have_a_nested_structure(levels=4)
        repo_path = os.path.join(current_dir, repo_name)

        And.I_have_a_git_repository_called(repo_path)
        When.I_have_a_Mr_Repo_repository(clean=True)
        And.I_execute_the_following_input("update")
        Then.I_have_updated_config_files(
                config_check=RepossesserStories.__config_has_new_repo(
                    repo_name),
                repo_check=RepossesserStories.__repo_has_new_repo(repo_name))

    def test_update_stops_searching_at_max_level(self):
        pass

    # TODO: Add more stories!
