USER="eyJpc3MiOiAiaHR0cHM6Ly9hdXRoLmdhdGV3YXktMzktZGV2LXBhc3MtdXNlci0wNWxzamMuY2kuZXhwaG9zdC5wbC9kZXgiLCAic3ViIjogIkNnZDBaWE4wTFhCeUVnUnNaR0Z3IiwgImF1ZCI6ICJleHBob3N0LWNvbnRyb2xsZXIiLCAiZXhwIjogMTY1MjE4MDM1MywgImlhdCI6IDE2NTIwOTM5NTMsICJhdF9oYXNoIjogIjc1a0NUUkRxTFFMU19XWjgyVUtXZGciLCAiZW1haWwiOiAidGVzdC1wckBtYWlsLnJ1IiwgImVtYWlsX3ZlcmlmaWVkIjogdHJ1ZSwgImdyb3VwcyI6IFsidGVzdC11c2VyIiwgInRlc3Qtb3JnIl0sICJuYW1lIjogInRlc3QtdXNlciJ9" # noqa


def test_create_instance(client, app):
    response = client.post(
        "/instances/",
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
        "values": {
            "newkey": "newvalue"
        }
    }
    assert instances == expected


def test_create_instance_already_exists(client):
    response = client.post(
        "/instances/",
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
        "/instances/",
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
        "/instances/?org=test-org&app=app1",
        headers={'Authorization': 'Bearer ' + USER})
    assert response.status_code == 200
    assert response.json == {
        "master": {
            "values": {}
        },
        "some-values": {
            "values": {
                "key1": "value1"
            }
        }
    }
