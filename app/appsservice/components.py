from flask import Blueprint, request, current_app
from flask_restx import Api, Resource, fields
from .helpers import has_access_to_org, required_fields

bp = Blueprint('components', __name__, url_prefix='/api/apps/v1/components')
authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}
api = Api(bp, authorizations=authorizations, security='apikey')

component_model = api.model(
    'Component',
    {
        'helm': fields.Raw(),
        'dockerfile': fields.Raw(),
        'config': fields.Raw(),
    }
)


@api.route('/', endpoint='components')
class Components(Resource):
    @api.expect(component_model, validate=True)
    @has_access_to_org
    @required_fields(['org', 'app', 'name', 'spec'])
    def post(self):
        org = request.json['org']
        app = request.json['app']
        name = request.json['name']
        spec = request.json['spec']
        try:
            current_app.dao.save_component(org, app, name, spec)
        except FileNotFoundError as e:
            return {'message': str(e)}, 404
        return {}, 201
