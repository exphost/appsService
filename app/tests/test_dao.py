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
        'org': 'test-org',
        'config': {
            'domain': 'test-org-app1.domain.com'
        },
        'components': {
            'frontend': {
                'helm': {
                    'type': 'nginx',
                    'chart': {
                        'name': 'nginx',
                        'repository': 'https://charts.bitnami.com/bitnami',
                        'version': '15.10.3'
                    },
                },
                'dockerfile':                 {
                    'type': 'react',
                },
                'config': {
                    'hostnames': [
                        'www',
                    ]
                },
                'values': {
                    'containerSecurityContext': {
                        'enabled': False
                    },
                    'service': {
                        'type': 'ClusterIP'
                    },
                    'ingress': {
                        'enabled': True,
                        'hostname': 'www.test-org-app1.domain.com',
                        'extraHosts': [],
                        'path': '/',
                    }
                },
            },
            'backend': {
                'helm': {
                    'type': 'simple',
                    'chart': {
                        'name': 'nginx',
                        'repository': 'https://charts.bitnami.com/bitnami',
                        'version': '15.10.3'
                    },
                },
                'dockerfile': {
                    'type': 'python',
                },
                'config': {
                    'hostnames': [
                        'api',
                    ],
                },
            },
            'backend2': {
                'helm': {
                    'type': 'custom',
                    'chart': {
                        'name': 'nginx',
                        'repository': 'https://charts.bitnami.com/bitnami',
                        'version': '15.10.3'
                    },
                },
                'dockerfile': {
                    'type': 'custom',
                },
                'config': {
                    'hostnames': [
                        'app2',
                    ],
                },
            },
        },
    }
    assert expected == get_app


def test_get_app_version(app):
    get_app = app.dao.get_app(org="test-org", app="app1", version="v1.2.3")
    expected = {
        'name': 'app1',
        'org': 'test-org',
        'config': {
            'domain': 'test-org-app1-version.domain.com'
        },
        'components': {
            'frontend': {
                'helm': {
                    'type': 'simple',
                    'chart': {
                        'name': 'nginx',
                        'repository': 'https://charts.bitnami.com/bitnami',
                        'version': '15.10.3'
                    },
                },
                'dockerfile':                 {
                    'type': 'react',
                },
                'config': {
                    'hostnames': [
                        'www',
                    ]
                },
            },
            'backend': {
                'helm': {
                    'type': 'simple',
                    'chart': {
                        'name': 'nginx',
                        'repository': 'https://charts.bitnami.com/bitnami',
                        'version': '15.10.3'
                    },
                },
                'dockerfile': {
                    'type': 'python',
                },
                'config': {
                    'hostnames': [
                        'api',
                    ],
                },
            },
            'backend2': {
                'helm': {
                    'type': 'custom',
                    'chart': {
                        'name': 'nginx',
                        'repository': 'https://charts.bitnami.com/bitnami',
                        'version': '15.10.3'
                    },
                },
                'dockerfile': {
                    'type': 'custom',
                },
                'config': {
                    'hostnames': [
                        'app2',
                    ],
                },
            },
        },
    }
    assert expected == get_app


def test_app_not_found(app):
    with pytest.raises(FileNotFoundError):
        app.dao.get_app(org="test-org", app="app4")


def test_add_component(app):
    app.dao.create_app(org="test-org", app="app4")
    app.dao.save_component(org="test-org", app="app4", name="frontend", spec={
       "helm": {
           "type": "nginx"
       },
       "version": "20231213-12150001",
       "dockerfile": None,
       "config": {
           "hostnames": [
               "www",
           ],
       },
    })
    get_app = app.dao.get_app(org="test-org", app="app4")["components"]["frontend"] # noqa E501
    expected = {
        "helm": {
            "type": "nginx",
            "chart": {
                "name": "nginx",
                "repository": "https://charts.bitnami.com/bitnami",
                "version": "15.10.3"
            },
        },
        "version": "20231213-12150001",
        "dockerfile": None,
        "config": {
            "hostnames": [
                "www",
            ]
        },
    }
    get_app.pop('values')
    assert expected == get_app


def test_update_app(app):
    app.dao.create_app(
        org="test-org",
        app="app3",
        spec={"config": {'domain': 'example.com'}}
    )
    app.dao.save_component(
        org="test-org",
        app="app3",
        name="frontned",
        spec={
            "helm": {
                "type": "nginx"
            },
            "version": "20231213-12150001",
            "dockerfile": None,
            "config": {
                "hostnames": [
                    "www",
                ],
            },
        }
    )
    app.dao.save_app(
        org="test-org",
        app="app3",
        spec={
            "config": {
                'domain': 'example.io'
            },
        }
    )
    get_app = app.dao.get_app(org="test-org", app="app3")["config"]
    expected = {
        'domain': 'example.io'
    }
    assert expected == get_app


def test_update_component(app):
    app.dao.create_app(org="test-org", app="app3")
    app.dao.save_component(
        org="test-org",
        app="app3",
        name="frontned",
        spec={
            "helm": {
                "type": "nginx"
            },
            "version": "20231213-12150001",
            "dockerfile": None,
            "config": {
                "hostnames": [
                    "www",
                ],
            },
        }
    )
    app.dao.save_component(
        org="test-org",
        app="app3",
        name="frontend",
        spec={
            "helm": {
                "type": "nginx"
            },
            "version": "20231213-12150003",
            "dockerfile": None,
            "config": {
                "hostnames": [
                    "www2",
                ],
            },
        })
    get_app = app.dao.get_app(org="test-org", app="app3")["components"]["frontend"] # noqa E501
    expected = {
        "helm": {
            "type": "nginx",
            "chart": {
                "name": "nginx",
                "repository": "https://charts.bitnami.com/bitnami",
                "version": "15.10.3"
            },
        },
        "version": "20231213-12150003",
        "dockerfile": None,
        "config": {
            "hostnames": [
                "www2",
            ],
        },
    }
    get_app.pop('values')
    assert expected == get_app


def test_delete_component(app):
    ret = app.dao.delete_component(
        org="test-org",
        app="app1",
        name="frontend")
    assert ret is True
    get_app = app.dao.get_app(org="test-org", app="app1")["components"]
    expected = {
       'backend': {
           'helm': {
               'type': 'simple',
               'chart': {
                   'name': 'nginx',
                   'repository': 'https://charts.bitnami.com/bitnami',
                   'version': '15.10.3'
               },
           },
           'dockerfile': {
               'type': 'python',
           },
           'config': {
               'hostnames': [
                   'api',
               ],
           },
       },
       'backend2': {
           'helm': {
               'type': 'custom',
               'chart': {
                   'name': 'nginx',
                   'repository': 'https://charts.bitnami.com/bitnami',
                   'version': '15.10.3'
               },
           },
           'dockerfile': {
               'type': 'custom',
           },
           'config': {
               'hostnames': [
                   'app2',
               ],
           },
       },
    }
    assert expected == get_app


def test_save_component_non_existing_app(app):
    with pytest.raises(FileNotFoundError):
        app.dao.save_component(
            org="test-org3",
            app="app5",
            name="frontend",
            spec={
                "helm": {
                    "type": "nginx"
                },
                "version": "20231213-12150001",
                "dockerfile": None,
                "config": {
                    "hostnames": [
                        "www",
                    ],
                },
            })


def test_delete_component_non_existing_app(app):
    with pytest.raises(FileNotFoundError):
        app.dao.delete_component(
            org="test-org3",
            app="app5",
            name="frontend")


def test_delete_component_non_existing_component(app):
    ret = app.dao.delete_component(
        org="test-org",
        app="app1",
        name="frontend2")
    assert ret is False


def test_get_component(app):
    component = app.dao.get_component(
        org="test-org",
        app="app1",
        name="frontend")
    assert type(component["helm"]) == dict


def test_get_component_non_existing_component(app):
    with pytest.raises(FileNotFoundError):
        app.dao.get_component(
            org="test-org",
            app="app1",
            name="frontend2")


def test_get_component_non_existing_app(app):
    with pytest.raises(FileNotFoundError):
        app.dao.get_component(
            org="test-org",
            app="app5",
            name="frontend")


def test_create_app_yaml(app):
    apppath = app.dao._app_dir(org="test-org")
    app.dao.create_app(
        org="test-org",
        app="app5",
        spec={
            "config": {
                "domain": "example.com"
            }
        })

    assert os.path.exists(apppath)
    appfile = os.path.join(apppath, "test-org.app5.yml")
    assert os.path.exists(appfile)

    manifest = yaml.load(
        open(appfile).read(),
        Loader=yaml.UnsafeLoader)
    expected = yaml.safe_load("""
apiVersion: exphost.pl/v1alpha1
kind: Application
metadata:
    name: test-org.app5
    namespace: test-namespace
    labels:
        org: test-org
        app: app5
spec:
    config:
        domain: example.com
    components: {}
""")
    assert expected == manifest


def test_create_app_with_component_yaml(app):
    apppath = app.dao._app_dir(org="test-org")
    app.dao.create_app(
        org="test-org",
        app="app5",
        spec={
            "config": {
                "domain": "example.com"
            }
        })
    app.dao.save_component(
        org="test-org",
        app="app5",
        name="nginx1",
        spec={
            "helm": {
                "type": "nginx"
            },
            "version": "1.2.3",
        })

    assert os.path.exists(apppath)
    appfile = os.path.join(apppath, "test-org.app5.yml")
    assert os.path.exists(appfile)

    manifest = yaml.load(
        open(appfile).read(),
        Loader=yaml.UnsafeLoader)
    expected = yaml.safe_load("""
apiVersion: exphost.pl/v1alpha1
kind: Application
metadata:
    name: test-org.app5
    namespace: test-namespace
    labels:
        org: test-org
        app: app5
spec:
    config:
        domain: example.com
    components:
        nginx1:
            helm:
                type: nginx
                chart:
                    name: nginx
                    repository: https://charts.bitnami.com/bitnami
                    version: 15.10.3
            version: 1.2.3
""")
    manifest['spec']['components']['nginx1'].pop('values')
    assert expected == manifest


def test_list_app_versions(app):
    versions = app.dao.list_app_versions(org="test-org", app="app1")
    assert len(versions) == 2
    assert versions[0] == 'v0.0.*-exphost-dev'
    assert versions[1] == "v1.2.3"


def test_make_version(app):
    app.dao.make_version(org="test-org", app="app1", version="v1.2.4")
    versions = app.dao.list_app_versions(org="test-org", app="app1")
    assert len(versions) == 3
    assert versions[0] == 'v0.0.*-exphost-dev'
    assert versions[1] == "v1.2.3"
    assert versions[2] == "v1.2.4"


def test_list_app_versions_empty(app):
    versions = app.dao.list_app_versions(org="test-org", app="app1")
    assert len(versions) == 2
    assert versions[0] == 'v0.0.*-exphost-dev'
    assert versions[1] == "v1.2.3"
