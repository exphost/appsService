USER="eyJpc3MiOiAiaHR0cHM6Ly9hdXRoLmdhdGV3YXktMzktZGV2LXBhc3MtdXNlci0wNWxzamMuY2kuZXhwaG9zdC5wbC9kZXgiLCAic3ViIjogIkNnZDBaWE4wTFhCeUVnUnNaR0Z3IiwgImF1ZCI6ICJleHBob3N0LWNvbnRyb2xsZXIiLCAiZXhwIjogMTY1MjE4MDM1MywgImlhdCI6IDE2NTIwOTM5NTMsICJhdF9oYXNoIjogIjc1a0NUUkRxTFFMU19XWjgyVUtXZGciLCAiZW1haWwiOiAidGVzdC1wckBtYWlsLnJ1IiwgImVtYWlsX3ZlcmlmaWVkIjogdHJ1ZSwgImdyb3VwcyI6IFsidGVzdC11c2VyIiwgInRlc3Qtb3JnIl0sICJuYW1lIjogInRlc3QtdXNlciJ9" # noqa


def test_components_add(client, app):
    response = client.post(
        '/api/apps/v1/components/',
        json={
            'org': 'test-org',
            'app': 'app1',
            'name': 'add',
            'spec': {
                'helm': {
                    'type': 'nginx',
                },
                'dockerfile': None,
                'config': {
                    'hostnames': ['www']
                }
            }
        },
        headers={'Authorization': 'Bearer ' + USER})
    assert response.status_code == 201

    component = app.dao.get_component(
        org="test-org",
        app="app1",
        name="add",
        )
    expected = {
        'helm': {
            'type': 'nginx',
            'chart': {
                'name': 'nginx',
                'repository': 'https://charts.bitnami.com/bitnami',
                'version': '15.10.3'
            }
        },
        'dockerfile': None,
        'config': {
            'hostnames': ['www']
        }
    }
    assert expected == component


def test_components_add_non_existing_app(client, app):
    response = client.post(
        '/api/apps/v1/components/',
        json={'org': 'test-org',
              'app': 'app10',
              'name': 'add-app1',
              'spec': {}},
        headers={'Authorization': 'Bearer ' + USER})
    assert response.status_code == 404


def test_components_add_missing_app_name(client):
    response = client.post(
        '/api/apps/v1/components/',
        json={'org': 'test-org',
              'name': 'test-app'},
        headers={'Authorization': 'Bearer ' + USER})
    assert response.status_code == 400


def test_components_add_missing_component_name(client):
    response = client.post(
        '/api/apps/v1/components/',
        json={'org': 'test-org',
              'app': 'app1'},
        headers={'Authorization': 'Bearer ' + USER})
    assert response.status_code == 400


def test_components_add_not_logged(client):
    response = client.post(
        '/api/apps/v1/components/',
        json={'org': 'test-org',
              'app': 'app1',
              'name': 'test-app'})
    assert response.status_code == 401


def test_components_add_wrong_org(client):
    response = client.post(
        '/api/apps/v1/components/',
        json={'org': 'another-org',
              'app': 'app1',
              'name': 'add-app'},
        headers={'Authorization': 'Bearer ' + USER})
    assert response.status_code == 403


def test_component_list_by_type(client, app):
    response = client.get(
        '/api/apps/v1/components/?org=test-org&app=app1&type=nginx',
        headers={'Authorization': 'Bearer ' + USER})
    assert response.status_code == 200
    assert len(response.json) == 1
    assert 'frontend' in response.json


def test_component_get(client, app):
    response = client.get(
        '/api/apps/v1/components/?org=test-org&app=app1&name=frontend',
        headers={'Authorization': 'Bearer ' + USER})
    assert response.status_code == 200
    assert response.json == {
        'helm': {
            'type': 'nginx',
            'chart': {
                'name': 'nginx',
                'repository': 'https://charts.bitnami.com/bitnami',
                'version': '15.10.3'
            }
        },
        'dockerfile': {
            'type': 'react'
        },
        'config': {
            'hostnames': ['www']
        }
    }
