import pytest
from appsservice import create_app
import os
import shutil
from unittest.mock import patch


@pytest.fixture
def app():
    os.environ['USERS_DOMAIN'] = "users.example.com"
    os.environ['AUTHSERVICE_ENDPOINT'] = "https://auth.example.com"
    shutil.copytree("tests/files", "workdir", dirs_exist_ok=True)
    with patch('appsservice.helpers.requests.post') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'claims': {
                'groups': ['test-org']
            }
        }
        app = create_app()
        yield app
    shutil.rmtree("workdir")


@pytest.fixture
def client(app):
    return app.test_client()
