from pea import step, TestCase, Given, When, Then, And, world
from mr_repo import MrRepo
import os
import git
import tempfile
import shutil


@step
def the_following_input(given_input):
    world.given_str = given_input


@step
def I_parse_the_input():
    world.mr_repo.parse_args(world.given_str.split())


@step
def I_setup_files():
    world.mr_repo.setup_files()
    if not world.mr_repo.is_init:
        world.mr_repo.read_config()


@step
def I_execute_the_command():
    result = world.mr_repo.execute()
    assert isinstance(result, str)


@step
def I_have_mr_repo_config_files():
    assert os.path.isfile(world.mr_repo.config_path)
    assert world.mr_repo.config_file.writeable()
    assert None != world.mr_repo.config.get('repos')
    assert os.path.isfile(world.mr_repo.repo_file_path)
    assert world.mr_repo.repo_file_path.writeable()
    assert isinstance(world.mr_repo.repos.get('repos'), list)


@step
def there_is_a_git_repository_called(repo_name, bare=False):
    tdir = tempfile.mkdtemp()
    repo_dir = os.path.join(tdir, repo_name)
    world.git_repo = git.Repo.init(repo_dir, bare=bare)


@step
def I_add_the_repository(repo_path):
    world.mr_repo.args.path = repo_path
    world.mr_repo.add_command()


@step
def mr_repo_updates_config_files():
    pass


class MrRepoStories(TestCase):
    """Some test cases for Mr. Repo."""

    def setUp(self):
        """Setup MrRepoStories tests."""
        super(MrRepoStories, self).setUp()
        world.mr_repo = MrRepo()

    def test_running_init_creates_files(self):
        """When init is run, the config files are created and they are
        normal."""
        Given.the_following_input('init')
        When.I_parse_the_input()
        And.I_setup_files()
        And.I_execute_the_command()
        Then.I_have_mr_repo_config_files()

    def test_adding_a_git_repo():
        Given.there_is_a_git_repository_called("shoes")
        When.I_add_the_repository(world.git_repo.working_dir)
        Then.mr_repo_updates_config_files()

    def tearDown(self):
        super(MrRepoStories, self).tearDown()
        world.mr_repo = None
        if isinstance(world.git_repo, git.Repo):
            shutil.rmtree(world.git_repo.working_dir)
