import pytest
from appsservice import create_app
import os
import git
import shutil


@pytest.fixture
def app():
    git.Repo.init("/tmp/qqq", bare=True)
    os.environ['GIT_REPO'] = "/tmp/qqq"
    app = create_app()
    yield app
    shutil.rmtree("/tmp/qqq")
    shutil.rmtree("workdir")


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def example_apps(app):
    os.makedirs("workdir/test-org/apps", exist_ok=True)
    with open("workdir/test-org/apps/test-app.yml", "w") as file:
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
    with open("workdir/test-org/apps/another-app.yml", "w") as file:
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
