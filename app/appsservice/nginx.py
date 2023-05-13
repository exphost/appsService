from flask import Blueprint, request, current_app
from flask_restx import Api, Resource, fields
from .helpers import auth_required, has_access_to_org

bp = Blueprint('nginx', __name__, url_prefix='/nginx')
api = Api(bp, doc='/')

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
        'app_name': fields.String(
            description="App name",
            required=True,
            example="app1"
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
        'app_name': fields.String(
            description="App name",
            required=False,
            example="app1"
        ),
    }
)


@api.route("/", endpoint="nginx")
class Nginx(Resource):
    @api.expect(nginx_model, validate=True)
    @auth_required
    @has_access_to_org
    def post(self):
        dao = current_app.dao
        try:
            dao.get_app(request.json['org'], request.json['app_name'])
        except FileNotFoundError:
            return {'error': 'app not found'}, 404
        try:
            dao.get_component(
                request.json['org'],
                request.json['app_name'],
                request.json['name'])
            return {'error': 'component already exists'}, 409
        except FileNotFoundError:
            pass
        try:
            values = self._params_to_helm_values(request)
        except ValueError as e:
            return {'error': str(e)}, 400
        values['_type'] = "nginx"
        component = {
            "name": "nginx",
            "releaseName": request.json['name'],
            "repo": "https//gitlab.exphost.pl/charts",
            "version": "10.0.1",
            "valuesInline": values,
        }
        if not dao.update_component(
                request.json['org'],
                request.json['app_name'],
                component):
            return {'error': 'failed to update component'}, 500
        return {'status': 'created'}, 201

    @auth_required
    @has_access_to_org
    def get(self):
        org = request.args.get('org', None)
        app_name = request.args.get('app_name', None)
        if not app_name:
            return {'error': 'no app_name provided'}, 400
        try:
            components = current_app.dao.get_app(org, app_name)
        except FileNotFoundError:
            return {'error': 'app not found'}, 404
        nginxs = list(map(
            self._helm_values_to_params,
            filter(
                lambda x: x['valuesInline']['_type'] == 'nginx',
                components)))
        print(nginxs)
        return {'nginx': nginxs}

    def _params_to_helm_values(self, request):
        values = {}
        hostname = "{name}.{org}.{domain}".format(
                    name=request.json['name'],
                    org=request.json['org'],
                    domain=current_app.config['USERS_DOMAIN']
                    )
        values['service'] = {'type': 'ClusterIP'}
        values['ingress'] = {'enabled': True,
                             'hostname': hostname,
                             'tls': True,
                             'certManager': True,
                             'annotations': {
                               'cert-manager.io/cluster-issuer': 'acme-issuer'
                               }
                             }
        fqdns = request.json.get('fqdns', None)
        if fqdns:
            values['ingress']['extraHosts'] = []
            for f in fqdns:
                values['ingress']['extraHosts'].append({
                    'name': f,
                    'path': '/'
                    })
        git = request.json.get('git', None)
        if git:
            if not git.get('repo', None):
                raise ValueError("Repo is not defined")
            branch = git.get('branch', 'master')
            values['cloneStaticSiteFromGit'] = {'enabled': True,
                                                'repository': git['repo'],
                                                'branch': branch}
        return values

    def _helm_values_to_params(self, values):
        def get_fqdns(values):
            if not values:
                return []
            hosts = [values.get('hostname'), ]
            hosts += [i['name'] for i in values.get('extraHosts', [])]
            return hosts

        result = {'name': values['releaseName']}
        values_mapping = [
            (('git', 'repo'), ('cloneStaticSiteFromGit', 'repository')),
            (('git', 'branch'), ('cloneStaticSiteFromGit', 'branch')),
            (('fqdns',), ('ingress',), get_fqdns)
        ]
        for mapping in values_mapping:
            tmp_value = values['valuesInline']
            for k in mapping[1][:-1]:
                tmp_value = tmp_value.get(k, {})
            tmp_value = tmp_value.get(mapping[1][-1], "__SKIP__")
            if tmp_value == "__SKIP__":
                continue
            if len(mapping) > 2:
                tmp_value = mapping[2](tmp_value)

            tmp_key = result
            for k in mapping[0][:-1]:
                if k not in tmp_key:
                    tmp_key[k] = {}
                tmp_key = tmp_key[k]
            tmp_key[mapping[0][-1]] = tmp_value
        return result
