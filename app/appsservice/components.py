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
    @has_access_to_org
    @required_fields(['org', 'app'])
    def get(self):
        org = request.args.get('org')
        app = request.args.get('app')
        try:
            components = current_app.dao.get_components(org, app)
        except FileNotFoundError as e:
            return {'message': str(e)}, 404
        if request.args.get('name'):
            name = request.args.get('name')
            return components.get(name, {}), 200
        if request.args.get('type'):
            type = request.args.get('type')
            return {k: v for k, v in components.items() if v.get('helm', {}).get('type') == type}, 200  # noqa E501
        return components

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
