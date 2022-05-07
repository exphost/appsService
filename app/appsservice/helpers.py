from flask import request


def auth_required(fn):
    def wrapper(*args, **kwargs):
        if not request.headers.get('X-User', None):
            return {'error': 'Not authenticated'}, 401
        return fn(*args, **kwargs)
    return wrapper


def git_pull(app):
    app.config['gitsem'].acquire()
    repo = app.config['repo']
    repo.remotes.origin.pull()
    app.config['gitsem'].release()
