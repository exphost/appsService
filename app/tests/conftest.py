import pytest
from appsservice import create_app
import os
import git
import shutil


def get_path_temp_dir(subpath=""):
    return os.path.join(os.path.realpath(os.path.curdir), "temp_dir", subpath)


def gitinit():
    git.Repo.init(os.environ['GIT_REPO'], bare=True)


@pytest.fixture
def app():
    shutil.rmtree(get_path_temp_dir(), ignore_errors=True)
    shutil.rmtree("workdir", ignore_errors=True)

    os.environ['GIT_REPO'] = get_path_temp_dir("repo")
    os.environ['USERS_DOMAIN'] = "users.example.com"
    gitinit()
    example_apps()
    app = create_app()
    example_apps2()
    app.dao.list_apps("test-org")
    yield app
    shutil.rmtree(get_path_temp_dir())
    shutil.rmtree("workdir")


@pytest.fixture
def set_subpath():
    os.environ['GIT_SUBPATH'] = 'tenants'


@pytest.fixture
def app_with_subpath(set_subpath, app):
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def client_with_subpath(app_with_subpath):
    return app_with_subpath.test_client()


def example_apps():
    p = get_path_temp_dir("update1")
    repo = git.Repo.clone_from(os.environ['GIT_REPO'], p)
    shutil.copytree("tests/files/phase1", p, dirs_exist_ok=True)
    repo.index.add(p+"/apps")
    repo.index.commit("example apps")
    repo.remotes.origin.push().raise_if_error()


def example_apps2():
    p = get_path_temp_dir("update2")
    repo = git.Repo.clone_from(os.environ['GIT_REPO'], p)
    shutil.copytree("tests/files/phase2", p, dirs_exist_ok=True)
    repo.index.add(p+"/apps")
    repo.index.add(p+"/instances")
    repo.index.commit("example apps2")
    repo.remotes.origin.push().raise_if_error()
