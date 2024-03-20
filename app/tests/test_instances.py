USER="eyJpc3MiOiAiaHR0cHM6Ly9hdXRoLmdhdGV3YXktMzktZGV2LXBhc3MtdXNlci0wNWxzamMuY2kuZXhwaG9zdC5wbC9kZXgiLCAic3ViIjogIkNnZDBaWE4wTFhCeUVnUnNaR0Z3IiwgImF1ZCI6ICJleHBob3N0LWNvbnRyb2xsZXIiLCAiZXhwIjogMTY1MjE4MDM1MywgImlhdCI6IDE2NTIwOTM5NTMsICJhdF9oYXNoIjogIjc1a0NUUkRxTFFMU19XWjgyVUtXZGciLCAiZW1haWwiOiAidGVzdC1wckBtYWlsLnJ1IiwgImVtYWlsX3ZlcmlmaWVkIjogdHJ1ZSwgImdyb3VwcyI6IFsidGVzdC11c2VyIiwgInRlc3Qtb3JnIl0sICJuYW1lIjogInRlc3QtdXNlciJ9" # noqa


def test_create_instance_no_version(client, app):
    response = client.post(
        "/api/apps/v1/instances/",
        json={
            "org": "test-org",
            "app": "test-app",
            "name": "newinstance",
            "config": {
                "values": {
                    "newkey": "newvalue"
                }
            }
        },
        headers={'Authorization': 'Bearer ' + USER})
    assert response.status_code == 201
    instances = app.dao.get_instance("test-org", "test-app", "newinstance")
    expected = {
        "version": "v0.0.*-exphost-dev",
        "values": {
            "newkey": "newvalue"
        }
    }
    assert instances == expected


def test_create_instance_version(client, app):
    response = client.post(
        "/api/apps/v1/instances/",
        json={
            "org": "test-org",
            "app": "test-app",
            "name": "newinstance2",
            "config": {
                "version": "v2.1.7",
                "values": {
                    "newkey": "newvalue"
                }
            }
        },
        headers={'Authorization': 'Bearer ' + USER})
    assert response.status_code == 201
    instances = app.dao.get_instance("test-org", "test-app", "newinstance2")
    expected = {
        "version": "v2.1.7",
        "values": {
            "newkey": "newvalue"
        }
    }
    assert instances == expected


def test_create_instance_already_exists(client):
    response = client.post(
        "api/apps/v1/instances/",
        json={
            "org": "test-org",
            "app": "app1",
            "name": "master2",
            "config": {
                "values": {
                    "newkey": "newvalue"
                }
            }
        },
        headers={'Authorization': 'Bearer ' + USER})
    assert response.status_code == 201
    response = client.post(
        "/api/apps/v1/instances/",
        json={
            "org": "test-org",
            "app": "app1",
            "name": "master2",
            "config": {
                "values": {
                    "newkey": "newvalue"
                }
            }
        },
        headers={'Authorization': 'Bearer ' + USER})
    assert response.status_code == 409


def test_get_instances(client):
    response = client.get(
        "/api/apps/v1/instances/?org=test-org&app=app1",
        headers={'Authorization': 'Bearer ' + USER})
    assert response.status_code == 200
    assert response.json == {
        "master": {
            "values": {},
            "version": "v1.0.1",
        },
        "some-values": {
            "version": "v0.0.*-exphost-dev",
            "values": {
                "key1": "value1"
            }
        }
    }


def test_get_instances_new_app(client):
    response = client.get(
        "/api/apps/v1/instances/?org=test-org&app=app2",
        headers={'Authorization': 'Bearer ' + USER})
    assert response.status_code == 200
    assert response.json == {}
