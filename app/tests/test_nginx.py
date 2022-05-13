import yaml


USER="eyJpc3MiOiAiaHR0cHM6Ly9hdXRoLmdhdGV3YXktMzktZGV2LXBhc3MtdXNlci0wNWxzamMuY2kuZXhwaG9zdC5wbC9kZXgiLCAic3ViIjogIkNnZDBaWE4wTFhCeUVnUnNaR0Z3IiwgImF1ZCI6ICJleHBob3N0LWNvbnRyb2xsZXIiLCAiZXhwIjogMTY1MjE4MDM1MywgImlhdCI6IDE2NTIwOTM5NTMsICJhdF9oYXNoIjogIjc1a0NUUkRxTFFMU19XWjgyVUtXZGciLCAiZW1haWwiOiAidGVzdC1wckBtYWlsLnJ1IiwgImVtYWlsX3ZlcmlmaWVkIjogdHJ1ZSwgImdyb3VwcyI6IFsidGVzdC11c2VyIiwgInRlc3Qtb3JnIl0sICJuYW1lIjogInRlc3QtdXNlciJ9" # noqa


def test_nginx_add(client):
    response = client.post(
        '/nginx/',
        json={'org': 'test-org',
              'name': 'add-app'},
        headers={'X-User-Full': USER})
    assert response.status_code == 201
    with open("workdir/test-org/apps/add-app.yml", "r") as file:
        application = yaml.safe_load(file)
    assert application['kind'] == "Application"
    assert application['metadata']['name'] == "add-app"
    assert application['metadata']['namespace'] == "argocd"
    assert application['spec']['destination']['namespace'] == "tenant-test-org"
    assert application['spec']['project'] == "tenant-test-org"
    source = application['spec']['source']
    assert source['chart'] == "nginx"
    assert source['targetRevision'] == "10.0.1"
    assert source['helm']
    assert source['repoURL'] == "https://charts.bitnami.com/bitnami"

    with open("workdir/test-org/project.yml", "r") as file:
        project = yaml.safe_load(file)
    assert project['kind'] == "AppProject"
    assert project['metadata']['name'] == "tenant-test-org"
    assert project['metadata']['namespace'] == "argocd"
    assert project['spec']['destinations'] == [{'namespace': 'tenant-test-org',
                                                'server': '*'
                                                }]


def test_nginx_add_static_page(client):
    response = client.post(
        '/nginx/',
        json={'org': 'test-org',
              'name': 'add-app',
              'git': {'repo': 'https://github.com/example/example.git',
                      'branch': 'devel'},
              'fqdn': 'example.example.com'},
        headers={'X-User-Full': USER})
    assert response.status_code == 201
    with open("workdir/test-org/apps/add-app.yml", "r") as file:
        application = yaml.safe_load(file)
    assert application['kind'] == "Application"
    assert application['metadata']['name'] == "add-app"
    assert application['metadata']['namespace'] == "argocd"
    assert application['spec']['destination']['namespace'] == "tenant-test-org"
    assert application['spec']['project'] == "tenant-test-org"
    source = application['spec']['source']
    assert source['chart'] == "nginx"
    assert source['targetRevision'] == "10.0.1"
    assert source['helm']
    assert source['repoURL'] == "https://charts.bitnami.com/bitnami"
    values = yaml.safe_load(source['helm']['values'])
    assert values['ingress']['enabled']
    assert values['ingress']['hostname'] == "example.example.com"
    assert values['service']['type'] == "ClusterIP"
    git_val = values['cloneStaticSiteFromGit']
    assert git_val['enabled']
    assert git_val['repository'] == 'https://github.com/example/example.git'
    assert git_val['branch'] == 'devel'


def test_nginx_add_static_page_default_branch(client):
    response = client.post(
        '/nginx/',
        json={'org': 'test-org',
              'name': 'add-app',
              'git': {'repo': 'https://github.com/example/example.git'},
              'fqdn': 'example.example.com'},
        headers={'X-User-Full': USER})
    assert response.status_code == 201
    with open("workdir/test-org/apps/add-app.yml", "r") as file:
        application = yaml.safe_load(file)
    source = application['spec']['source']
    values = yaml.safe_load(source['helm']['values'])
    git_val = values['cloneStaticSiteFromGit']
    assert git_val['enabled']
    assert git_val['repository'] == 'https://github.com/example/example.git'
    assert git_val['branch'] == 'master'


def test_nginx_add_static_page_missing_repo(client):
    response = client.post(
        '/nginx/',
        json={'org': 'test-org',
              'name': 'add-app',
              'git': {'branch': 'devel'},
              'fqdn': 'example.example.com'},
        headers={'X-User-Full': USER})
    assert response.status_code == 400


def test_nginx_add_duplicate(client):
    response = client.post(
        '/nginx/',
        json={'org': 'test-org',
              'name': 'add-app'},
        headers={'X-User-Full': USER})
    assert response.status_code == 201
    response = client.post(
        '/nginx/',
        json={'org': 'test-org',
              'name': 'add-app'},
        headers={'X-User-Full': USER})
    assert response.status_code == 409


def test_nginx_add_missing_name(client):
    response = client.post(
        '/nginx/',
        json={'name': 'test-app'})
    assert response.status_code == 400


def test_nginx_add_not_logged(client):
    response = client.post(
        '/nginx/',
        json={'org': 'test-org',
              'name': 'test-app'})
    assert response.status_code == 401


def test_nginx_list(client):
    response = client.get(
        '/nginx/?org=test-org',
        headers={'X-User-Full': USER})
    assert response.status_code == 200
    assert 'nginx' in response.json
    assert len(response.json['nginx']) == 3
    apps = sorted(response.json['nginx'], key=lambda x: x['name'])
    assert apps[0]['name'] == "another-app"
    assert apps[1]['name'] == "new-app"
    assert 'fqdn' not in apps[1]
    assert 'git' not in apps[1]
    assert apps[2]['name'] == "test-app"
    assert apps[2]['git']['repo'] == "https://github.com/example/example.git"
    assert apps[2]['git']['branch'] == "master"
    assert apps[2]['fqdn'] == "www.example.com"

    response = client.get(
        '/nginx/?org=test-org',
        headers={'X-User-Full': USER})
    assert response.status_code == 200


def test_nginx_list_empty_org(client):
    response = client.get(
        '/nginx/?org=test-user',
        headers={'X-User-Full': USER})
    assert response.status_code == 200
    assert 'nginx' in response.json
    assert len(response.json['nginx']) == 0


def test_nginx_list_no_org(client):
    response = client.get(
        '/nginx/',
        headers={'X-User-Full': USER})
    assert response.status_code == 400


def test_nginx_list_not_logged(client):
    response = client.get(
        '/nginx/?org=test-org')
    assert response.status_code == 401


def test_nginx_add_wrong_org(client):
    response = client.post(
        '/nginx/',
        json={'org': 'another-org',
              'name': 'add-app'},
        headers={'X-User-Full': USER})
    assert response.status_code == 403


def test_nginx_list_wrong_org(client):
    response = client.get(
        '/nginx/?org=another-org',
        headers={'X-User-Full': USER})
    assert response.status_code == 403


def test_nginx_list_with_prefix(client_with_subpath):
    response = client_with_subpath.get(
        '/nginx/?org=test-org',
        headers={'X-User-Full': USER})
    assert response.status_code == 200
    assert 'nginx' in response.json
    assert len(response.json['nginx']) == 1
    apps = sorted(response.json['nginx'], key=lambda x: x['name'])
    assert apps[0]['name'] == "new-app2"
    assert 'fqdn' not in apps[0]
    assert 'git' not in apps[0]


def test_nginx_add_with_prefix(client_with_subpath):
    response = client_with_subpath.post(
        '/nginx/',
        json={'org': 'test-org',
              'name': 'add-app3'},
        headers={'X-User-Full': USER})
    assert response.status_code == 201
    with open("workdir/tenants/test-org/apps/add-app3.yml", "r") as file:
        application = yaml.safe_load(file)
    assert application['kind'] == "Application"
    assert application['metadata']['name'] == "add-app3"
    assert application['metadata']['namespace'] == "argocd"
    assert application['spec']['destination']['namespace'] == "tenant-test-org"
    assert application['spec']['project'] == "tenant-test-org"
    source = application['spec']['source']
    assert source['chart'] == "nginx"
    assert source['targetRevision'] == "10.0.1"
    assert source['helm']
    assert source['repoURL'] == "https://charts.bitnami.com/bitnami"

    with open("workdir/tenants/test-org/project.yml", "r") as file:
        project = yaml.safe_load(file)
    assert project['kind'] == "AppProject"
    assert project['metadata']['name'] == "tenant-test-org"
    assert project['metadata']['namespace'] == "argocd"
    assert project['spec']['destinations'] == [{'namespace': 'tenant-test-org',
                                                'server': '*'
                                                }]
