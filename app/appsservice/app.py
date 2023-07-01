from flask import Blueprint, request, current_app
from flask_restx import Api, Resource, fields
from .helpers import auth_required, has_access_to_org

bp = Blueprint('app', __name__, url_prefix='/app')
api = Api(bp, doc='/')

app_model = api.model(
    'App',
    {
        'org': fields.String(required=True),
        'name': fields.String(required=True),
    })

app_model_list = api.model(
    'App',
    {
        'org': fields.String(required=True),
    })


@api.route('/', endpoint='app')
class App(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dao = current_app.dao

    @api.expect(app_model, validate=True)
    @auth_required
    @has_access_to_org
    def post(self):
        try:
            if self.dao.get_app(request.json['org'], request.json['name']):
                return {'message': 'App already exists'}, 409
        except FileNotFoundError:
            pass

        self.dao.save_app(request.json['org'], request.json['name'], [])
        return {'status': 'created'}, 201

    @auth_required
    @has_access_to_org
    def get(self):
        return self.dao.list_apps(org=request.args['org'])
