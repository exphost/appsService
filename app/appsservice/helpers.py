from flask import request, current_app
import requests


def has_access_to_org(fn):
    def wrapper(*args, **kwargs):
        if not request.headers.get('Authorization', None):
            return {'error': 'Not authenticated'}, 401
        claims_response = requests.post(
            current_app.config['AUTHSERVICE_ENDPOINT'] + '/api/auth/v1/token/validate',  # noqa E501
            headers={'Authorization': request.headers['Authorization']}
        )
        if claims_response.status_code != 200:
            return {'error': 'Not authenticated'}, 401
        groups = claims_response.json()['claims']['groups']

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


def required_fields(fields):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            for field in fields:
                if request.method == "POST":
                    if field not in request.json:
                        return {'message': f'Missing field {field}'}, 400
                elif request.method == "GET":
                    if field not in request.args:
                        return {'message': f'Missing field {field}'}, 400
            return fn(*args, **kwargs)
        return wrapper
    return decorator
