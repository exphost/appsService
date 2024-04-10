import yaml
import os


def test_get_instance(app):
    instance = app.dao.get_instance("test-org", "app1", "master")
    expected = {
            "version": "v1.0.1",
            "values": {}
    }
    assert instance == expected


def test_get_instance_with_values(app):
    instance = app.dao.get_instance("test-org", "app1", "some-values")
    expected = {
            "version": "v0.0.*-exphost-dev",
            "values": {
                "key1": "value1",
            }
    }
    assert instance == expected


def test_get_instances(app):
    instances = app.dao.get_instances("test-org", "app1")
    expected = {
        "master": {
            "version": "v1.0.1",
            "values": {}
        },
        "some-values": {
            "version": "v0.0.*-exphost-dev",
            "values": {
                "key1": "value1",
            }
        }
    }
    assert instances == expected


def test_get_instances_non_existing_org(app):
    instances = app.dao.get_instances("non-existing-org", "app1")
    assert instances == {}


def test_get_instances_non_existing_app(app):
    instances = app.dao.get_instances("test-org", "non-existing-app")
    assert instances == {}


def test_create_instance_manifest_content(app):
    instance = {
        "version": "v1.0.1",
        "values": {
            "key2": "value2",
        }
    }
    app.dao.create_instance("test-org", "app1", "instance1", instance)
    with open(os.path.join(app.dao.workdir, "instances", "test-org", "app1", "instance1.yml"), "r") as f:  # noqa E501
        content = yaml.safe_load(f)
    expected = yaml.safe_load("""apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: test-org-app1-instance1
  namespace: argocd
  labels:
    org: test-org
    app: app1
    instance: instance1
spec:
  destination:
    namespace: test-org-app1-instance1
    server: https://kubernetes.default.svc
  project: default
  source:
    chart: test-org.app1
    helm:
      values: |
        key2: value2
    repoURL: https://chart2.exphost.pl
    targetRevision: "v1.0.1"
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
""")
    assert content == expected
