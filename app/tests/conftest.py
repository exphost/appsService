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
    example_apps3()
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
    app1_subpath = "test-org/app1/base"
    app1_path = os.path.join(p, app1_subpath)
    os.makedirs(app1_path, exist_ok=True)
    with open(os.path.join(app1_path, "kustomization.yml"), "w") as file:
        file.write(
            open("tests/files/test-org/app1/base/kustomization.yml").read()
        )
    app2_path = os.path.join(p, "test-org/app2/base")
    os.makedirs(app2_path, exist_ok=True)
    with open(os.path.join(app2_path, "kustomization.yml"), "w") as file:
        file.write(
            open("tests/files/test-org/app2/base/kustomization.yml").read())
    repo.index.add("test-org/app1/base/kustomization.yml")
    repo.index.add("test-org/app2/base/kustomization.yml")
    repo.index.commit("example apps")
    repo.remotes.origin.push().raise_if_error()


def example_apps2():
    p = get_path_temp_dir("update2")
    repo = git.Repo.clone_from(os.environ['GIT_REPO'], p)
    app1_path = os.path.join(p, "test-org/app1/base")
    app2_path = os.path.join(p, "test-org2/app1/base")
    with open(os.path.join(app1_path, "kustomization.yml"), "w") as file:
        file.write(
            open("tests/files/test-org/app1/base/kustomization2.yml").read())
    os.makedirs(app2_path, exist_ok=True)
    with open(os.path.join(app2_path, "kustomization.yml"), "w") as file:
        file.write(
            open("tests/files/test-org2/app1/base/kustomization.yml").read())
    repo.index.add("test-org/app1/base/kustomization.yml")
    repo.index.add("test-org2/app1/base/kustomization.yml")
    repo.index.commit("example apps2")
    repo.remotes.origin.push().raise_if_error()


def example_apps3():
    p = get_path_temp_dir("update3")
    repo = git.Repo.clone_from(os.environ['GIT_REPO'], p)
    app1_path = os.path.join(p, "test-org/app1/base")
    with open(os.path.join(app1_path, "kustomization.yml"), "w") as file:
        file.write(
            open("tests/files/test-org/app1/base/kustomization3.yml").read())
    repo.index.add("test-org/app1/base/kustomization.yml")
    repo.index.commit("example apps3")
    repo.remotes.origin.push().raise_if_error()
