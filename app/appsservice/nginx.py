from flask import Blueprint, request, current_app
from flask_restx import Api, Resource, fields
from .helpers import has_access_to_org

bp = Blueprint('nginx', __name__, url_prefix='/api/apps/v1/nginx')
authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-User-Full'
    }
}
api = Api(bp, doc='/docs', authorizations=authorizations, security='apikey')

git_model = api.model(
    'Git',
    {
        'branch': fields.String(
            description="Static page git branch",
            required=False,
            example="devel"
        ),
        'repo': fields.String(
            description="Static page git repo",
            required=True,
            example="qwe"
        ),
    }
)
nginx_config_model = api.model(
  'NginxConfig',
  {
      'fqdns': fields.List(fields.String(
          description="fqdn of static page",
          required=True,
          example="example.example.com"
      )),
      'git': fields.Nested(git_model)
    }
)
nginx_model = api.model(
    'Nginx',
    {
        'name': fields.String(
            description="component name",
            required=True,
            example="test-nginx"
        ),
        'org': fields.String(
            description="Organization that owns this app",
            required=True,
            example="test-org"
        ),
        'app': fields.String(
            description="App name",
            required=True,
            example="app1"
        ),
        'config': fields.Nested(nginx_config_model)
    }
)
nginx_query_model = api.model(
    'NginxQuery',
    {
        'org': fields.String(
            description="Organization that owns this app",
            required=True,
            example="test-org"
        ),
        'app': fields.String(
            description="App name",
            required=False,
            example="app1"
        ),
    }
)


@api.route("/", endpoint="nginx")
class Nginx(Resource):
    @api.expect(nginx_model, validate=True)
    @has_access_to_org
    def post(self):
        dao = current_app.dao
        try:
            dao.get_app(request.json['org'], request.json['app'])
        except FileNotFoundError:
            return {'error': 'app not found'}, 404
        try:
            dao.get_component(
                request.json['org'],
                request.json['app'],
                {
                    "name": request.json['name'],
                    "type": "nginx",
                })
            return {'error': 'component already exists'}, 409
        except FileNotFoundError:
            pass
        try:
            values = self._params_to_helm_values(request)
        except ValueError as e:
            return {'error': str(e)}, 400
        component = {
            "type": "nginx",
            "name": request.json['name'],
            "repo": "https://charts.bitnami.com/bitnami",
            "chart": "nginx",
            "version": "15.1.2",
            "values": values
        }
        try:
            dao.save_component(
                request.json['org'],
                request.json['app'],
                component)
            return {'status': 'created'}, 201
        except FileNotFoundError:
            return {'error': 'app not found'}, 500

    @has_access_to_org
    def get(self):
        org = request.args.get('org', None)
        app_name = request.args.get('app', None)
        if not app_name:
            return {'error': 'no app provided'}, 400
        try:
            components = current_app.dao.get_app(org, app_name)['components']
        except FileNotFoundError:
            return {'error': 'app not found'}, 404
        nginxs = list(map(
            self._helm_values_to_params,
            filter(
                lambda x: x['type'] == 'nginx',
                components)))
        print("NGINXS: ", nginxs)
        return {'nginx': nginxs}

    def _params_to_helm_values(self, request):
        values = {}
        config = request.json.get('config', {})
        hostname = f"{request.json['name']}-{request.json['app']}.{request.json['org']}.{current_app.config['USERS_DOMAIN']}"  # noqa E501
        values['service'] = {'type': 'ClusterIP'}
        values['ingress'] = {
            'enabled': True,
            'hostname': hostname,
            'tls': True,
            'certManager': True,
            'annotations': {
              'cert-manager.io/cluster-issuer': 'acme-issuer'
              }
            }
        fqdns = config.get('fqdns', None)
        if fqdns:
            values['ingress']['extraHosts'] = []
            for f in fqdns:
                values['ingress']['extraHosts'].append({
                    'name': f,
                    'path': '/'
                    })
        git = config.get('git', None)
        if git:
            if not git.get('repo', None):
                raise ValueError("Repo is not defined")
            branch = git.get('branch', 'master')
            values['cloneStaticSiteFromGit'] = {
                'enabled': True,
                'repository': git['repo'],
                'branch': branch
            }
        return values

    def _helm_values_to_params(self, component):
        values = component['values']
        print("VALUES: ", values)
        git = values.get('cloneStaticSiteFromGit', None)
        if git:
            git = {
                'repo': git['repository'],
                'branch': git['branch']
            }
        return {
            'name': component['name'],
            'config': {
                'fqdns': [values['ingress']['hostname']] + list(map(lambda x: x['name'], values['ingress'].get('extraHosts', []))),  # noqa E501
                'git': git
            }
        }
