from flask import Blueprint, request, current_app
from flask_restx import Api, Resource, fields
import os
import jinja2
from .helpers import auth_required
from .common import create_project_if_needed

bp = Blueprint('nginx', __name__, url_prefix='/nginx')
api = Api(bp, doc='/')

nginx_model = api.model(
    'Nginx',
    {
        'name': fields.String(
            description="App name",
            required=True,
            example="test-nginx"
        ),
        'org': fields.String(
            description="Organization that owns this app",
            required=True,
            example="test-org"
        ),
    }
)


@api.route("/", endpoint="nginx")
class Nginx(Resource):
    @api.expect(nginx_model, validate=True)
    @auth_required
    def post(self):
        gitdir = current_app.config['gitdir']
        ingitpath = os.path.join(
            request.json['org'],
            "apps",
            request.json['name']+".yml"
        )
        apppath = os.path.join(
            gitdir,
            ingitpath
        )
        if os.path.exists(apppath):
            return "App already exists", 409
        with open("appsservice/templates/application_helm.j2", "r") as file:
            template = jinja2.Template(file.read())
        app = template.render(
            name=request.json['name'],
            org=request.json['org'],
            namespace="tenant-" + request.json['org'],
            project="tenant-" + request.json['org'],
            chart="nginx",
            version="10.0.1",
            repo="https://charts.bitnami.com/bitnami",
        )
        os.makedirs(os.path.dirname(apppath), exist_ok=True)
        current_app.config['gitsem'].acquire()
        create_project_if_needed(request.json['org'],
                                 current_app.config['repo'],
                                 gitdir)
        with open(apppath, 'w') as file:
            file.write(app)
        repo = current_app.config['repo']
        repo.index.add(ingitpath)
        repo.index.commit("add nginx")
        ssh_cmd = current_app.config['ssh_cmd']
        with repo.git.custom_environment(GIT_SSH_COMMAND=ssh_cmd):
            repo.remotes.origin.push().raise_if_error()
        current_app.config['gitsem'].release()
        return "Created", 201
