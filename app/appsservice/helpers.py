from flask import request
import json
import base64


def auth_required(fn):
    def wrapper(*args, **kwargs):
        if not request.headers.get('X-User-Full', None):
            return {'error': 'Not authenticated'}, 401
        return fn(*args, **kwargs)
    return wrapper


def has_access_to_org(fn):
    def wrapper(*args, **kwargs):
        groups = request.headers.get('X-User-Full')
        groups = json.loads(base64.b64decode(groups))['groups']
        if request.method == "POST":
            org = request.json['org']
        elif request.method == "GET":
            org = request.args['org']
        else:
            return {'error': 'Method not implemented'}, 501
        if org not in groups:
            return {'error': 'Org not permitted'}, 403
        return fn(*args, **kwargs)
    return wrapper
