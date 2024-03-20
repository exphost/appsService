from flask import Blueprint, request, current_app
from flask_restx import Api, Resource, fields
from .helpers import has_access_to_org, required_fields


bp = Blueprint('versions', __name__, url_prefix='/api/apps/v1/versions')
authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}
api = Api(bp, authorizations=authorizations, security='apikey')

version_model = api.model(
    'Version',
    {
        'version': fields.String(),
    }
)


@api.route('/', endpoint='versions')
class Versions(Resource):
    @api.expect(version_model, validate=True)
    @has_access_to_org
    @required_fields(['org', 'app', 'version'])
    def post(self):
        org = request.json['org']
        app = request.json['app']
        version = request.json['version']
        try:
            current_app.dao.make_version(org, app, version)
        except FileNotFoundError:
            return {}, 404
        except FileExistsError:
            return {}, 409
        except Exception:
            return {}, 450
        return {}, 201

    @has_access_to_org
    @required_fields(['org', 'app'])
    def get(self):
        org = request.args.get('org')
        app = request.args.get('app')
        versions = current_app.dao.list_app_versions(org, app)
        return {'versions': versions}
