from flask import Flask
import git
import os
from . import nginx
import threading


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        GIT_REPO=os.environ.get("GIT_REPO", "")
    )
    if not app.config['GIT_REPO']:
        app.logger.error("GIT_REPO not provided")
        return False
    app.config['git_subpath'] = os.environ.get("GIT_SUBPATH", "")
    app.config['gitdir'] = "workdir"
    app.config['ssh_cmd'] = ("ssh "
                             "-o StrictHostKeyChecking=no "
                             "-o UserKnownHostsFile=/dev/null "
                             "-i /app/sshkey/id_rsa"
                             )
    repo = git.Repo.clone_from(app.config['GIT_REPO'],
                               app.config['gitdir'],
                               env=dict(GIT_SSH_COMMAND=app.config['ssh_cmd']))
    app.config['repo'] = repo
    app.config['gitsem'] = threading.Semaphore()

    app.register_blueprint(nginx.bp)
    return app
