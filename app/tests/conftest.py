import pytest
from appsservice import create_app
import os
import shutil


@pytest.fixture
def app():
    os.environ['USERS_DOMAIN'] = "users.example.com"
    shutil.copytree("tests/files", "workdir", dirs_exist_ok=True)
    app = create_app()
    yield app
    shutil.rmtree("workdir")


@pytest.fixture
def client(app):
    return app.test_client()
