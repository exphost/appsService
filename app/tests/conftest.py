import pytest
from appsservice import create_app
import os
import git
import shutil


@pytest.fixture
def app():
    git.Repo.init("/tmp/qqq", bare=True)
    os.environ['GIT_REPO'] = "/tmp/qqq"
    app = create_app()
    yield app
    shutil.rmtree("/tmp/qqq")
    shutil.rmtree("workdir")


@pytest.fixture
def client(app):
    return app.test_client()
