USER="eyJpc3MiOiAiaHR0cHM6Ly9hdXRoLmdhdGV3YXktMzktZGV2LXBhc3MtdXNlci0wNWxzamMuY2kuZXhwaG9zdC5wbC9kZXgiLCAic3ViIjogIkNnZDBaWE4wTFhCeUVnUnNaR0Z3IiwgImF1ZCI6ICJleHBob3N0LWNvbnRyb2xsZXIiLCAiZXhwIjogMTY1MjE4MDM1MywgImlhdCI6IDE2NTIwOTM5NTMsICJhdF9oYXNoIjogIjc1a0NUUkRxTFFMU19XWjgyVUtXZGciLCAiZW1haWwiOiAidGVzdC1wckBtYWlsLnJ1IiwgImVtYWlsX3ZlcmlmaWVkIjogdHJ1ZSwgImdyb3VwcyI6IFsidGVzdC11c2VyIiwgInRlc3Qtb3JnIl0sICJuYW1lIjogInRlc3QtdXNlciJ9" # noqa


def test_create_app(client, app):
    resposne = client.post(
        "/app/",
        json={
            'org': 'test-org',
            'name': 'test-app',
        },
        headers={'Authorization': 'Bearer ' + USER})
    assert resposne.status_code == 201
    # not exception means app exists
    app.dao.get_app(org='test-org', app='test-app')


def test_list_apps(client, app):
    response = client.get(
        "/app/?org=test-org",
        headers={'Authorization': 'Bearer ' + USER})
    assert response.status_code == 200
    assert len(response.json) == 2
    assert response.json[0] == 'app1'
    assert response.json[1] == 'app2'
