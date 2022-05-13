import pytest
from appsservice import create_app
import os
import git
import shutil


def gitinit():
    git.Repo.init("/tmp/qqq", bare=True)


@pytest.fixture
def app():
    gitinit()
    os.environ['GIT_REPO'] = "/tmp/qqq"
    example_apps()
    app = create_app()
    example_apps2()
    example_apps3()
    yield app
    shutil.rmtree("/tmp/qqq")
    shutil.rmtree("/tmp/qqq2")
    shutil.rmtree("/tmp/qqq3")
    shutil.rmtree("/tmp/qqq4")
    shutil.rmtree("workdir")


@pytest.fixture
def set_subpath():
    os.environ['GIT_SUBPATH'] = 'tenants'


@pytest.fixture
def app_with_subpath(set_subpath, app):
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def client_with_subpath(app_with_subpath):
    return app_with_subpath.test_client()


def example_apps():
    repo = git.Repo.clone_from("/tmp/qqq",
                               "/tmp/qqq2")
    os.makedirs("/tmp/qqq2/test-org/apps", exist_ok=True)
    with open("/tmp/qqq2/test-org/apps/test-app.yml", "w") as file:
        file.write("""
---
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: test-app
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: tenant-test-org
  source:
    repoURL: https://charts.bitnami.com/bitnami
    targetRevision: 10.0.1
    chart: nginx
    helm:
      values: |-
        {'service': {'type': 'ClusterIP'}, 'ingress': {'enabled': True, 'hostname': 'www.example.com', 'tls': True}, 'cloneStaticSiteFromGit': {'enabled': True, 'repository': 'https://github.com/example/example.git', 'branch': 'master'}}

  destination:
    server: 'https://kubernetes.default.svc'
    namespace: tenant-test-org
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
""") # noqa
    repo.index.add("test-org/apps/test-app.yml")
    with open("/tmp/qqq2/test-org/apps/another-app.yml", "w") as file:
        file.write("""
---
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: another-app
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: tenant-test-org
  source:
    repoURL: https://charts.bitnami.com/bitnami
    targetRevision: 10.0.1
    chart: nginx
    helm:
      values: |-

  destination:
    server: 'https://kubernetes.default.svc'
    namespace: tenant-test-org
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
""")
    repo.index.add("test-org/apps/another-app.yml")
    repo.index.commit("example apps")
    repo.remotes.origin.push().raise_if_error()


def example_apps2():
    repo = git.Repo.clone_from("/tmp/qqq",
                               "/tmp/qqq3")
    os.makedirs("/tmp/qqq3/test-org/apps", exist_ok=True)
    with open("/tmp/qqq3/test-org/apps/new-app.yml", "w") as file:
        file.write("""
---
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: new-app
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: tenant-test-org
  source:
    repoURL: https://charts.bitnami.com/bitnami
    targetRevision: 10.0.1
    chart: nginx
    helm:
      values: |-

  destination:
    server: 'https://kubernetes.default.svc'
    namespace: tenant-test-org
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
""")
    repo.index.add("test-org/apps/new-app.yml")
    repo.index.commit("new apps")
    repo.remotes.origin.push().raise_if_error()


def example_apps3():
    repo = git.Repo.clone_from("/tmp/qqq",
                               "/tmp/qqq4")
    os.makedirs("/tmp/qqq4/tenants/test-org/apps", exist_ok=True)
    with open("/tmp/qqq4/tenants/test-org/apps/new-app2.yml", "w") as file:
        file.write("""
---
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: new-app2
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: tenant-test-org
  source:
    repoURL: https://charts.bitnami.com/bitnami
    targetRevision: 10.0.1
    chart: nginx
    helm:
      values: |-

  destination:
    server: 'https://kubernetes.default.svc'
    namespace: tenant-test-org
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
""")
    repo.index.add("tenants/test-org/apps/new-app2.yml")
    repo.index.commit("new apps2")
    repo.remotes.origin.push().raise_if_error()
