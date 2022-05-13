from flask import Blueprint, request, current_app
from flask_restx import Api, Resource, fields
import os
import jinja2
import glob
import yaml
from .helpers import auth_required, git_pull, has_access_to_org
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
        'git_repo': fields.String(
            description="Static page git repository",
            required=False,
            example="https://github.com/example/example.git"
        ),
    }
)
nginx_query_model = api.model(
    'Nginx',
    {
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
    @has_access_to_org
    def post(self):
        git_pull(current_app)
        gitdir = current_app.config['gitdir']
        ingitpath = os.path.join(
            current_app.config['git_subpath'],
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
        try:
            values = self._generate_values(request)
        except ValueError as e:
            return str(e), 400
        app = template.render(
            name=request.json['name'],
            org=request.json['org'],
            namespace="tenant-" + request.json['org'],
            project="tenant-" + request.json['org'],
            chart="nginx",
            version="10.0.1",
            repo="https://charts.bitnami.com/bitnami",
            values=values
        )
        os.makedirs(os.path.dirname(apppath), exist_ok=True)
        current_app.config['gitsem'].acquire()
        create_project_if_needed(current_app.config['git_subpath'],
                                 request.json['org'],
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

    @auth_required
    @has_access_to_org
    def get(self):
        git_pull(current_app)
        org = request.args.get('org', None)
        if not org:
            return {'error': 'no org provided'}, 400
        orgdir = os.path.join(
            current_app.config['gitdir'],
            current_app.config['git_subpath'],
            org)
        if not os.path.exists(orgdir):
            return {'nginx': [], 'status': 'org does not exists'}
        nginx = self._list_nginx_apps(orgdir)
        return {'nginx': nginx}

    def _generate_values(self, request):
        values = {}
        values['service'] = {'type': 'ClusterIP'}
        fqdn = request.json.get('fqdn', None)
        if fqdn:
            values['ingress'] = {'enabled': True,
                                 'hostname': fqdn,
                                 'tls': True}
        git = request.json.get('git', None)
        if git:
            if not git.get('repo', None):
                raise ValueError("Repo is not defined")
            branch = git.get('branch', 'master')
            values['cloneStaticSiteFromGit'] = {'enabled': True,
                                                'repository': git['repo'],
                                                'branch': branch}
        return values

    def _list_nginx_apps(self, orgdir):
        nginx = []
        for file in glob.glob(orgdir+"/apps/*.yml"):
            with open(file, "r") as f:
                app = yaml.safe_load(f)
            r_values = yaml.safe_load(app['spec']['source']['helm']['values'])
            values = self._map_app_to_values(r_values) if r_values else {}
            print("VAL: ", values)
            nginx.append({'name': app['metadata']['name'], **values})
        return nginx

    def _map_app_to_values(self, values):
        result = {}
        values_mapping = [
            (('git', 'repo'), ('cloneStaticSiteFromGit', 'repository')),
            (('git', 'branch'), ('cloneStaticSiteFromGit', 'branch')),
            (('fqdn',), ('ingress', 'hostname')),
        ]
        for mapping in values_mapping:
            tmp_value = values
            for k in mapping[1][:-1]:
                tmp_value = tmp_value.get(k, {})
            tmp_value = tmp_value.get(mapping[1][-1], "__SKIP__")
            if tmp_value == "__SKIP__":
                continue
            tmp_key = result
            for k in mapping[0][:-1]:
                if k not in tmp_key:
                    tmp_key[k] = {}
                tmp_key = tmp_key[k]
            tmp_key[mapping[0][-1]] = tmp_value
        return result
