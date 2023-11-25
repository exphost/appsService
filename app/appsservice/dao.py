# import threading
import os
import yaml
import textwrap


class AppsDao(object):
    def __init__(self, workdir):
        self.workdir = workdir

    def _app_path(self, org, app):
        return os.path.join(
            self._app_dir(org, app),
            "Chart.yaml"
        )

    def _instance_path(self, org, app, instance):
        return os.path.join(
            self._instances_dir(org, app),
            f"{instance}.yml"
        )

    def _app_dir(self, org, app):
        return os.path.join(
            self.workdir,
            'apps',
            org,
            app
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

    def _component_name_to_manifest_name(self, app, org, component):
        return f"{{{{ printf \"%s-%s\" .Release.Name .Chart.Name | trunc 63 | trimSuffix \"-\" }}}}-{component['type']}---{component['name']}"  # noqa: E501

    def _manifest_name_to_component_name(self, manifest_name):
        return manifest_name.split('---')[1]

    def _component_to_dict(self, component):
        component_yaml = yaml.safe_load(component.replace("{{", "__"))
        cy = component_yaml

        return {
            "name": self._manifest_name_to_component_name(cy["metadata"]["name"]),  # noqa: E501
            "type": cy["metadata"]["annotations"]["exphost.pl/type"],
            "repo": cy["spec"]["source"]["repoURL"],
            "chart": cy["spec"]["source"]["chart"],
            "version": cy["spec"]["source"]["targetRevision"],
            "values": yaml.safe_load(cy["spec"]["source"]["helm"]["values"]),
        }

    def _dict_to_component_conent(self, app, org, component):
        return f"""---
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: {self._component_name_to_manifest_name(app, org, component)}
  namespace: argocd
  annotations:
    exphost.pl/type: {component['type']}
spec:
  project: tenant-{org}
  source:
    repoURL: {component['repo']}
    chart: {component['chart']}
    targetRevision: {component['version']}
    helm:
      values: |
{textwrap.indent(yaml.dump(component['values']), 8*' ')}
  destination:
    server: 'https://kubernetes.default.svc'
    namespace: tenant-test-org-app1
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
"""  # noqa: E501

    def list_apps(self, org):
        org_dir = os.path.join(self.workdir, 'apps', org)
        if not os.path.exists(org_dir):
            return []
        return [i for i in next(os.walk(org_dir))[1] if self._is_app(org, i)]

    def get_app(self, org, app):
        if not self._is_app(org, app):
            raise FileNotFoundError
        obj = None
        templates_dir = os.path.join(self._app_dir(org, app), "templates")
        with open(self._app_path(org, app)) as f:
            obj = yaml.safe_load(f.read())
        obj["components"] = []
        for root, dirs, files in os.walk(templates_dir):
            for file in files:
                if not file.endswith(".yml"):
                    continue
                with open(os.path.join(root, file)) as f:
                    obj["components"].append(self._component_to_dict(f.read()))
        obj["components"].sort(key=lambda x: x["name"])
        return obj

    def save_component(self, org, app, component):
        if not self._is_app(org, app):
            raise FileNotFoundError
        templates_path = os.path.join(self._app_dir(org, app), "templates")
        os.makedirs(templates_path, exist_ok=True)
        manifest_file_name = f"{component['type']}-{component['name']}.yml"
        manifest_path = os.path.join(templates_path, manifest_file_name)
        if os.path.exists(manifest_path):
            # use existing component values
            existing_component = self.get_component(org, app, component)
            # update component values with new values
            existing_component.update(component)
            component = existing_component
        with open(manifest_path, "w") as f:
            f.write(self._dict_to_component_conent(app, org, component))

    def delete_component(self, org, app, component):
        if not self._is_app(org, app):
            raise FileNotFoundError
        # if component file does not exist then it is already deleted
        try:
            self.get_component(org, app, component)
        except FileNotFoundError:
            return True
        # delete component file
        templates_path = os.path.join(self._app_dir(org, app), "templates")
        component_file_name = f"{component['type']}-{component['name']}.yml"
        component_file = os.path.join(templates_path, component_file_name)
        os.remove(component_file)

    def get_component(self, org, app, component):
        if not self._is_app(org, app):
            raise FileNotFoundError
        templates_path = os.path.join(self._app_dir(org, app), "templates")
        component_file_name = f"{component['type']}-{component['name']}.yml"
        component_file = os.path.join(templates_path, component_file_name)
        if not os.path.exists(component_file):
            raise FileNotFoundError
        component_content = open(component_file).read()
        return self._component_to_dict(component_content)

    def create_app(self, org, app):
        app_path = self._app_dir(org, app)
        chart_path = os.path.join(app_path, "Chart.yaml")
        os.makedirs(app_path, exist_ok=True)
        templates_path = os.path.join(app_path, "templates")
        os.makedirs(templates_path, exist_ok=True)
        with open(chart_path, "w") as f:
            f.write(f"""---
apiVersion: v2
name: { app }
type: application
version: v0.0.1
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
            raise FileNotFoundError
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
