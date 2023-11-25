import pytest
import yaml
import os


def test_list_apps(app):
    apps = app.dao.list_apps(org="test-org")
    assert len(apps) == 2
    assert set(apps) == set(["app1", "app2"])


def test_list_apps_empty_org(app):
    apps = app.dao.list_apps(org="test-org3")
    assert len(apps) == 0


def test_get_app(app):
    get_app = app.dao.get_app(org="test-org", app="app1")
    expected = {
        'name': 'app1',
        'components': [{
            'chart': 'generic-app',
            'repo': 'https://gitlab.exphost.pl/charts',
            'version': 'v0.0.0-3-ge9ad446',
            'name': 'app2',  # noqa E501
            'type': 'asd',
            'values': {
                'image': {
                    'repository': 'registry.gitlab.exphost.pl/onelink/onelink-frontend',  # noqa E501
                    'tag': 'v0.0.0-5-g2b2479d',
                }
            }
        }, {
            'chart': 'generic-app',
            'repo': 'https://gitlab.exphost.pl/charts',
            'version': 'v0.0.0-3-ge9ad446',
            'name': 'frontend',  # noqa E501
            'type': 'react',
            'values': {
                'image': {
                    'repository': 'registry.gitlab.exphost.pl/onelink/onelink-frontend',  # noqa E501
                    'tag': 'v0.0.0-5-g2b2479d',
                }
            }
        },
        ]
    }
    assert expected.items() <= get_app.items()


def test_app_not_found(app):
    with pytest.raises(FileNotFoundError):
        app.dao.get_app(org="test-org", app="app4")


def test_add_component(app):
    app.dao.create_app(org="test-org", app="app4")
    app.dao.save_component(org="test-org", app="app4", component={
        "chart": "nginx",
        "name": "frontend",
        "repo": "repo4",
        "version": "1.1.0",
        "type": "nginx",
        "values": {
        }
    })
    get_app = app.dao.get_app(org="test-org", app="app4")
    expected = {
        'components': [{
            "chart": "nginx",
            "repo": "repo4",
            "version": "1.1.0",
            "name": 'frontend',
            "type": "nginx",
            "values": {}
        }]
    }
    assert expected.items() <= get_app.items()


def test_update_app(app):
    app.dao.create_app(org="test-org", app="app3")
    app.dao.save_component(org="test-org", app="app3", component={
        "chart": "nginx",
        "name": "frontend",
        "repo": "repo4",
        "version": "1.1.0",
        "type": "nginx",
        "values": {}
    })
    app.dao.save_component(
        org="test-org",
        app="app3",
        component={
            "chart": "nginx",
            "name": "frontend",
            "repo": "repo5",
            "version": "1.2.0",
            "type": "nginx",
            "values": {}
        })
    get_app = app.dao.get_app(org="test-org", app="app3")
    expected = {
        "components": [{
            "name": 'frontend',  # noqa E501
            "chart": "nginx",
            "repo": "repo5",
            "version": "1.2.0",
            "type": "nginx",
            "values": {},
        }]
    }
    assert expected.items() <= get_app.items()


def test_delete_component(app):
    app.dao.delete_component(
        org="test-org",
        app="app1",
        component={"type": "react", "name": "frontend"})
    get_app = app.dao.get_app(org="test-org", app="app1")
    expected = {
        "components": [{
            'chart': 'generic-app',
            'repo': 'https://gitlab.exphost.pl/charts',
            'version': 'v0.0.0-3-ge9ad446',
            'name': 'app2',  # noqa E501
            'type': 'asd',
            'values': {
                'image': {
                    'repository': 'registry.gitlab.exphost.pl/onelink/onelink-frontend',  # noqa E501
                    'tag': 'v0.0.0-5-g2b2479d',
                }
            }
        }]
    }
    assert expected.items() <= get_app.items()


def test_update_component(app):
    app.dao.save_component(
        org="test-org",
        app="app1",
        component={
            "type": "react",
            "name": "frontend",
            "version": "1.1.0",
            "values": {
                "repository": "registry.gitlab.exphost.pl/onelink/onelink-frontend",  # noqa E501
                "tag": "1.2.0",
            },
        })
    components = app.dao.get_app(org="test-org", app="app1")['components']
    assert len(components) == 2
    assert components[1]["version"] == "1.1.0"
    assert components[1]["type"] == "react"


def test_save_component_non_existing_app(app):
    with pytest.raises(FileNotFoundError):
        app.dao.save_component(org="test-org3", app="app5", component={
            "type": "nginx",
            "name": "frontend",
        })


def test_delete_component_non_existing_app(app):
    with pytest.raises(FileNotFoundError):
        app.dao.delete_component(
            org="test-org3",
            app="app5",
            component={"type": "react", "name": "frontend"})


def test_delete_component_non_existing_component(app):
    app.dao.delete_component(
        org="test-org",
        app="app1",
        component={"type": "pelican", "name": "frontend"})


def test_get_component(app):
    component = app.dao.get_component(
        org="test-org",
        app="app1",
        component={
            "name": "app2",
            "type": "asd"
            })
    assert component["name"] == 'app2'
    assert component["repo"] == "https://gitlab.exphost.pl/charts"
    assert component["version"] == "v0.0.0-3-ge9ad446"


def test_get_component_non_existing_component(app):
    with pytest.raises(FileNotFoundError):
        app.dao.get_component(
            org="test-org",
            app="app1",
            component={
                "type": "pelican",
                "name": "frontend"
            })


def test_get_component_non_existing_app(app):
    with pytest.raises(FileNotFoundError):
        app.dao.get_component(
            org="test-org",
            app="app5",
            component={
                "type": "pelican",
                "name": "frontend"
            })


def test_create_app(app):
    apppath = app.dao._app_dir(org="test-org", app="app5")
    app.dao.create_app(org="test-org", app="app5")

    assert os.path.exists(apppath)
    assert os.path.exists(os.path.join(apppath, "Chart.yaml"))

    chart = yaml.safe_load(open(os.path.join(apppath, "Chart.yaml")).read())
    assert chart["apiVersion"] == "v2"
    assert chart["name"] == "app5"
    assert chart["type"] == "application"


def test_yaml_syntax(app):
    app.dao.save_component(org="test-org", app="app1", component={
        "name": "nginx1",
        "type": "nginx",
        "chart": "nginx",
        "repo": "https://charts.gitlab.io/",
        "version": "1.2.3",
        "values": {
            "key1": "value1",
            "key2": "value2",
        }
    })
    apppath = app.dao._app_dir(org="test-org", app="app1")
    assert os.path.exists(apppath)
    component_path = os.path.join(apppath, "templates", "nginx-nginx1.yml")
    assert os.path.exists(component_path)
    manifest = yaml.load(
        open(component_path).read().replace('{{', '__'),
        Loader=yaml.UnsafeLoader)
    expected = yaml.safe_load("""
kind: Application
apiVersion: argoproj.io/v1alpha1
metadata:
    name: __ printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" }}-nginx---nginx1
    namespace: argocd
    annotations:
        exphost.pl/type: nginx
spec:
  project: tenant-test-org
  source:
    repoURL: https://charts.gitlab.io/
    chart: nginx
    targetRevision: 1.2.3
    helm:
      values: |
        key1: value1
        key2: value2
  destination:
    namespace: tenant-test-org-app1
    server: https://kubernetes.default.svc
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
""")  # noqa E501
    assert expected == manifest

# test_create_app_already_exists
