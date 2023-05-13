from flask import Flask
import os
from . import nginx
from . import dao


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        GIT_REPO=os.environ.get("GIT_REPO", ""),
        USERS_DOMAIN=os.environ.get("USERS_DOMAIN", "")
    )
    if not app.config['GIT_REPO']:
        app.logger.error("GIT_REPO not provided")
        return False
    if not app.config['USERS_DOMAIN']:
        app.logger.error("USERS_DOMAIN not provided")
        return False
    app.config['git_subpath'] = os.environ.get("GIT_SUBPATH", "")
    app.dao = dao.AppsDao(app.config['GIT_REPO'], app.config['git_subpath'])

    app.register_blueprint(nginx.bp)
    return app
