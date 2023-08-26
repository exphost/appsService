from flask import Blueprint, request, current_app
from flask_restx import Api, Resource, fields
from .helpers import auth_required, has_access_to_org

bp = Blueprint("instances", __name__, url_prefix="/instances")
authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-User-Full'
    }
}
api = Api(bp, authorizations=authorizations, security='apikey', doc="/docs")

instance_model = api.model('Instance', {
    'org': fields.String(required=True, description='Organization name'),
    'app': fields.String(required=True, description='Application name'),
    'name': fields.String(required=True, description='Application name'),
    'config': fields.Raw(required=True, description='Instance configuration'),
})


@api.route("/", endpoint="instances")
class Instances(Resource):
    @api.expect(instance_model, validate=True)
    @auth_required
    @has_access_to_org
    def post(self):
        dao = current_app.dao
        name = request.json.get("name")
        json = request.json
        try:
            if dao.get_instance(json["org"], json["app"], name):
                return "Instance already exists", 409
        except FileNotFoundError:
            pass
        dao.create_instance(json["org"], json["app"], name, json["config"])
        return "Instance created", 201

    @auth_required
    @has_access_to_org
    def get(self):
        dao = current_app.dao
        args = request.args
        instances = dao.get_instances(args.get("org"), args.get("app"))
        return instances, 200
