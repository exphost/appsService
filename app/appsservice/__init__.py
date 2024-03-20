from flask import Flask
import os
from . import components
from . import app as app_blueprint
from . import instances
from . import dao
from . import versions


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        USERS_DOMAIN=os.environ.get("USERS_DOMAIN", ""),
        WORKDIR=os.environ.get("WORKDIR", "workdir"),
        AUTHSERVICE_ENDPOINT=os.environ.get("AUTHSERVICE_ENDPOINT", ""),
    )
    if not app.config['USERS_DOMAIN']:
        app.logger.error("USERS_DOMAIN not provided")
        return False
    if not app.config['AUTHSERVICE_ENDPOINT']:
        app.logger.error("AUTHSERVICE_ENDPOINT not provided")
        return False
    app.dao = dao.AppsDao(app.config['WORKDIR'])

    app.register_blueprint(components.bp)
    app.register_blueprint(app_blueprint.bp)
    app.register_blueprint(instances.bp)
    app.register_blueprint(versions.bp)
    return app
