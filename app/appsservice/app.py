from flask import Blueprint, request, current_app
from flask_restx import Api, Resource, fields
from .helpers import has_access_to_org

bp = Blueprint('app', __name__, url_prefix='/api/apps/v1/app')
authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-User-Full'
    }
}
api = Api(bp, doc='/docs', authorizations=authorizations, security='apikey')

app_model = api.model(
    'App',
    {
        'org': fields.String(required=True),
        'name': fields.String(required=True),
    })

app_model_list = api.model(
    'AppQuery',
    {
        'org': fields.String(required=True),
    })


@api.route('/', endpoint='app')
class App(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dao = current_app.dao

    @api.expect(app_model, validate=True)
    @has_access_to_org
    def post(self):
        try:
            if self.dao.get_app(request.json['org'], request.json['name']):
                return {'message': 'App already exists'}, 409
        except FileNotFoundError:
            pass

        self.dao.create_app(request.json['org'], request.json['name'])
        return {'status': 'created'}, 201

    @has_access_to_org
    def get(self):
        return self.dao.list_apps(org=request.args['org'])
