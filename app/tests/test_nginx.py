import yaml


def test_nginx_add(client):
    response = client.post(
        '/nginx/',
        json={'org': 'test-org',
              'name': 'test-app'},
        headers={'X-User': 'test_user'})
    assert response.status_code == 201
    with open("workdir/test-org/apps/test-app.yml", "r") as file:
        application = yaml.safe_load(file)
    assert application['kind'] == "Application"
    assert application['metadata']['name'] == "test-app"
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
    assert project['metadata']['name'] == "test-org"
    assert project['metadata']['namespace'] == "argocd"
    assert project['spec']['destinations'] == [{'namespace': 'tenant-test-org',
                                                'server': '*'
                                                }]


def test_nginx_add_duplicate(client):
    response = client.post(
        '/nginx/',
        json={'org': 'test-org',
              'name': 'test-app'},
        headers={'X-User': 'test_user'})
    assert response.status_code == 201
    response = client.post(
        '/nginx/',
        json={'org': 'test-org',
              'name': 'test-app'},
        headers={'X-User': 'test_user'})
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


def test_nginx_list(client, example_apps):
    response = client.get(
        '/nginx/?org=test-org',
        headers={'X-User': 'test_user'})
    assert response.status_code == 200
    assert 'nginx' in response.json
    assert len(response.json['nginx']) == 2
    assert response.json['nginx'][0]['name'] == "test-app"
    assert response.json['nginx'][1]['name'] == "another-app"

    response = client.get(
        '/nginx/?org=test-org',
        headers={'X-User': 'test_user'})
    assert response.status_code == 200


def test_nginx_list_empty_org(client, example_apps):
    response = client.get(
        '/nginx/?org=test-org2',
        headers={'X-User': 'test_user'})
    assert response.status_code == 200
    assert 'nginx' in response.json
    assert len(response.json['nginx']) == 0


def test_nginx_list_no_org(client, example_apps):
    response = client.get(
        '/nginx/',
        headers={'X-User': 'test_user'})
    assert response.status_code == 400


def test_nginx_list_not_logged(client):
    response = client.get(
        '/nginx/?org=test-org')
    assert response.status_code == 401
