
USER="eyJpc3MiOiAiaHR0cHM6Ly9hdXRoLmdhdGV3YXktMzktZGV2LXBhc3MtdXNlci0wNWxzamMuY2kuZXhwaG9zdC5wbC9kZXgiLCAic3ViIjogIkNnZDBaWE4wTFhCeUVnUnNaR0Z3IiwgImF1ZCI6ICJleHBob3N0LWNvbnRyb2xsZXIiLCAiZXhwIjogMTY1MjE4MDM1MywgImlhdCI6IDE2NTIwOTM5NTMsICJhdF9oYXNoIjogIjc1a0NUUkRxTFFMU19XWjgyVUtXZGciLCAiZW1haWwiOiAidGVzdC1wckBtYWlsLnJ1IiwgImVtYWlsX3ZlcmlmaWVkIjogdHJ1ZSwgImdyb3VwcyI6IFsidGVzdC11c2VyIiwgInRlc3Qtb3JnIl0sICJuYW1lIjogInRlc3QtdXNlciJ9" # noqa


def test_make_version(client, app):
    response = client.post(
        "/api/apps/v1/versions/",
        json={
            'org': 'test-org',
            'app': 'app1',
            'version': 'v2.1.1'
        },
        headers={'Authorization': 'Bearer ' + USER}
    )
    assert response.status_code == 201
    app_yaml = app.dao.list_app_versions('test-org', 'app1')
    assert 'v2.1.1' in app_yaml


def test_make_version_already_exists(client, app):
    response = client.post(
        "/api/apps/v1/versions/",
        json={
            'org': 'test-org',
            'app': 'app1',
            'version': 'v2.1.2'
        },
        headers={'Authorization': 'Bearer ' + USER})
    assert response.status_code == 201
    response = client.post(
        "/api/apps/v1/versions/",
        json={
            'org': 'test-org',
            'app': 'app1',
            'version': 'v2.1.2'
        },
        headers={'Authorization': 'Bearer ' + USER})
    assert response.status_code == 409


def test_make_version_no_app(client, app):
    response = client.post(
        "/api/apps/v1/versions/",
        json={
            'org': 'test-org',
            'version': 'v2.1.2'
        },
        headers={'Authorization': 'Bearer ' + USER})
    assert response.status_code == 400


def test_make_version_no_version(client, app):
    response = client.post(
        "/api/apps/v1/versions/",
        json={
            'org': 'test-org',
            'app': 'app1',
        },
        headers={'Authorization': 'Bearer ' + USER})
    assert response.status_code == 400


def test_list_versions(client, app):
    response = client.post(
        "/api/apps/v1/versions/",
        json={
            'org': 'test-org',
            'app': 'app2',
            'version': 'v2.1.3'
        },
        headers={'Authorization': 'Bearer ' + USER})
    assert response.status_code == 201
    response = client.get(
        "/api/apps/v1/versions/?org=test-org&app=app2",
        headers={'Authorization': 'Bearer ' + USER})
    assert response.status_code == 200
    assert response.json == {'versions': ['v0.0.*-exphost-dev', 'v2.1.3']}
