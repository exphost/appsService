# import threading
import os
import yaml


class AppsDao(object):
    def __init__(self, workdir):
        self.workdir = workdir

    def _app_path(self, org, app):
        return os.path.join(
            self._app_dir(org),
            f"{org}.{app}.yml"
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
        apps = []
        for f_name in [i for i in next(os.walk(org_dir))[2]]:
            apps.append(f_name.replace(f"{org}.", "").replace(".yml", ""))
        return apps

    def get_app(self, org, app):
        if not self._is_app(org, app):
            raise FileNotFoundError
        app_yaml = yaml.safe_load(open(self._app_path(org, app)).read())
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
        app_yaml["spec"]["components"][name].update(spec)
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

    def get_component(self, org, app, name):
        if not self._is_app(org, app):
            raise FileNotFoundError
        app_yaml = yaml.safe_load(open(self._app_path(org, app)).read())
        if not app_yaml["spec"].get("components", None):
            raise FileNotFoundError
        if not app_yaml["spec"]["components"].get(name, None):
            raise FileNotFoundError
        return app_yaml["spec"]["components"][name]

    def create_app(self, org, app, spec={}):
        os.makedirs(self._app_dir(org), exist_ok=True)
        with open(self._app_path(org, app), "w") as f:
            f.write(f"""---
apiVersion: exphost.pl/v1alpha1
kind: Application
metadata:
    name: {org}.{app}
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
  project: default
  source:
    path: apps/{ org }/{ app }
    repoURL: git@gitlab.exphost.pl:exphost-controller/test_tenants_repo.git
    targetRevision: HEAD
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
        with open(self._instance_path(org, app, instance)) as f:
            instance = yaml.safe_load(f.read())
        values = yaml.safe_load(instance.get("spec").get("source", {}).get("helm", {}).get("values", ""))  # noqa E501
        if not values:
            values = {}
        return {
            "values": values,
        }
