# import threading
import os
import yaml
import re
from .apps import nginx as nginx_app

APPS = {
    "nginx": nginx_app,
}


class AppsDao(object):
    def __init__(self, app):
        self.namespace = os.environ.get('NAMESPACE', None)
        if not self.namespace:
            self.namespace = open("/var/run/secrets/kubernetes.io/serviceaccount/namespace", "r").read()  # noqa E501
        self.workdir = app.config['WORKDIR']
        # get from current app
        self.chart_repo = app.config['CHART_REPO']

    def _app_path(self, org, app, version=None):
        version_suffix = f".{version}" if version else ""
        return os.path.join(
            self._app_dir(org),
            f"{org}.{app}{version_suffix}.yml"
        )

    def _instance_path(self, org, app, instance):
        return os.path.join(
            self._instances_dir(org, app),
            f"{instance}.yml"
        )

    def _app_dir(self, org):
        return os.path.join(
            self.workdir,
            'apps',
            org,
        )

    def _instances_dir(self, org, app):
        return os.path.join(
            self.workdir,
            'instances',
            org,
            app
        )

    def _is_app(self, org, app):
        return os.path.exists(self._app_path(org, app))

    def list_apps(self, org):
        org_dir = self._app_dir(org)
        if not os.path.exists(org_dir):
            return []
        apps = set()
        for f_name in [i for i in next(os.walk(org_dir))[2]]:
            tokens = re.split(rf"{org}\.([\w-]+)\..*yml", f_name)
            if len(tokens) > 1:
                apps.add(tokens[1])
        return sorted(apps)

    def get_app(self, org, app, version=None):
        if not self._is_app(org, app):
            raise FileNotFoundError
        app_yaml = yaml.safe_load(
            open(self._app_path(org, app, version)).read()
        )
        return {
            "name": app_yaml["metadata"]["labels"]["app"],
            "org": app_yaml["metadata"]["labels"]["org"],
            "config": app_yaml["spec"].get("config", {}),
            "components": app_yaml["spec"].get("components", {}),
        }

    def save_app(self, org, app, spec):
        if not self._is_app(org, app):
            raise FileNotFoundError
        app_yaml = yaml.safe_load(open(self._app_path(org, app)).read())
        app_yaml["spec"].update(spec)
        with open(self._app_path(org, app), "w") as f:
            f.write(yaml.dump(app_yaml))

    def save_component(self, org, app, name, spec):
        if not self._is_app(org, app):
            raise FileNotFoundError
        app_yaml = yaml.safe_load(open(self._app_path(org, app)).read())
        if not app_yaml["spec"].get("components", None):
            app_yaml["spec"]["components"] = {}
        if not app_yaml["spec"]["components"].get(name, None):
            app_yaml["spec"]["components"][name] = {}
        component = app_yaml["spec"]["components"][name]
        component.update(spec)
        if component.get("helm", None):
            helm = component["helm"]
            if helm.get("type", None) and not helm.get("chart", None):
                helm["chart"] = APPS[helm["type"]].prepare_chart(component)
            component["values"] = APPS[helm["type"]].prepare_values(component, app_yaml)  # noqa E501
        with open(self._app_path(org, app), "w") as f:
            f.write(yaml.dump(app_yaml))

    def delete_component(self, org, app, name):
        if not self._is_app(org, app):
            raise FileNotFoundError
        app_yaml = yaml.safe_load(open(self._app_path(org, app)).read())
        if not app_yaml["spec"].get("components", None):
            return
        app_yaml["spec"]["components"].pop(name, None)
        with open(self._app_path(org, app), "w") as f:
            f.write(yaml.dump(app_yaml))

    def get_components(self, org, app):
        if not self._is_app(org, app):
            raise FileNotFoundError
        app_yaml = yaml.safe_load(open(self._app_path(org, app)).read())
        return app_yaml["spec"].get("components", {})

    def get_component(self, org, app, name):
        components = self.get_components(org, app)
        if not components:
            raise FileNotFoundError
        if not components.get(name, None):
            raise FileNotFoundError
        return components[name]

    def create_app(self, org, app, spec={}):
        os.makedirs(self._app_dir(org), exist_ok=True)
        with open(self._app_path(org, app), "w") as f:
            f.write(f"""---
apiVersion: exphost.pl/v1alpha1
kind: Application
metadata:
    name: {org}.{app}
    namespace: {self.namespace}
    labels:
        org: {org}
        app: {app}
spec:
    config: {spec.get("config", {})}
    components: {spec.get("components", {})}
""")

    def create_instance(self, org, app, instance_name, instance):
        instance_path = self._instance_path(org, app, instance_name)
        os.makedirs(self._instances_dir(org, app), exist_ok=True)
        print("AAA: ", instance_path)
        with open(instance_path, "w") as f:
            print("BBB", yaml.dump(instance))
            f.write(f"""apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: { org }-{ app }-{ instance_name }
  namespace: argocd
  labels:
    org: { org }
    app: { app }
    instance: { instance_name }
spec:
  destination:
    namespace: { org }-{ app }-{ instance_name }
    server: https://kubernetes.default.svc
  project: { org }-{ app }
  source:
    chart: { org }.{ app }
    repoURL: {self.chart_repo}
    targetRevision: { instance.get('version', 'v0.0.*-exphost-dev') }
    helm:
      values: |
        { yaml.dump(instance['values']) }
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
""")

    def get_instances(self, org, app):
        if not os.path.exists(self._instances_dir(org, app)):
            return {}
        instances = {}
        for instance in next(os.walk(self._instances_dir(org, app)))[2]:
            instance = instance.replace(".yml", "")
            instances[instance] = self.get_instance(org, app, instance)
        return instances

    def get_instance(self, org, app, instance):
        if not os.path.exists(self._instance_path(org, app, instance)):
            raise FileNotFoundError
        # if file is empty
        if os.stat(self._instance_path(org, app, instance)).st_size == 0:
            raise FileNotFoundError
        with open(self._instance_path(org, app, instance)) as f:
            instance = yaml.safe_load(f.read())
        values = yaml.safe_load(instance.get("spec").get("source", {}).get("helm", {}).get("values", ""))  # noqa E501
        if not values:
            values = {}
        return {
            "values": values,
            "version": instance["spec"]["source"]["targetRevision"],
        }

    def make_version(self, org, app, version):
        # to create a new version, we just copy the app file to a new file
        # add label version with the version name
        # if version already exists, we raise an error
        if not os.path.exists(self._app_path(org, app)):
            raise FileNotFoundError
        if os.path.exists(self._app_path(org, app)):
            if os.path.exists(self._app_path(org, app, version)):
                raise FileExistsError
        with open(self._app_path(org, app)) as f:
            app_yaml = yaml.safe_load(f.read())
        app_yaml["metadata"]["labels"]["version"] = version
        with open(self._app_path(org, app, version), "w") as f:
            f.write(yaml.dump(app_yaml))

    def list_app_versions(self, org, app):
        org_dir = self._app_dir(org)
        if not os.path.exists(org_dir):
            return []
        versions = set()
        if os.path.exists(self._app_path(org, app)):
            versions.add("v0.0.*-exphost-dev")
        for f_name in [i for i in next(os.walk(org_dir))[2] if i.startswith(f"{org}.{app}")]:  # noqa E501
            tokens = re.split(rf"{org}\.{app}\.(.+)\.yml", f_name)
            if len(tokens) > 1:
                versions.add(tokens[1])
        return sorted(versions)
