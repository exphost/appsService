USER="eyJpc3MiOiAiaHR0cHM6Ly9hdXRoLmdhdGV3YXktMzktZGV2LXBhc3MtdXNlci0wNWxzamMuY2kuZXhwaG9zdC5wbC9kZXgiLCAic3ViIjogIkNnZDBaWE4wTFhCeUVnUnNaR0Z3IiwgImF1ZCI6ICJleHBob3N0LWNvbnRyb2xsZXIiLCAiZXhwIjogMTY1MjE4MDM1MywgImlhdCI6IDE2NTIwOTM5NTMsICJhdF9oYXNoIjogIjc1a0NUUkRxTFFMU19XWjgyVUtXZGciLCAiZW1haWwiOiAidGVzdC1wckBtYWlsLnJ1IiwgImVtYWlsX3ZlcmlmaWVkIjogdHJ1ZSwgImdyb3VwcyI6IFsidGVzdC11c2VyIiwgInRlc3Qtb3JnIl0sICJuYW1lIjogInRlc3QtdXNlciJ9" # noqa


def test_app_nginx_add(client, app):
    response = client.post(
        '/api/apps/v1/components/',
        headers={
            'Authorization': 'Bearer ' + USER,
            'Content-Type': 'application/json'
        },
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
                    'hostnames': ['www'],
                    'git': {
                        'repo': 'https://git.repo'
                    },
                    'raw_values': {
                        'aaa': 'bbb'
                    },
                }
            }
        })
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
            'hostnames': ['www'],
            'git': {
                'repo': 'https://git.repo'
            },
            'raw_values': {
                'aaa': 'bbb'
            },
        },
        'values': {
            'containerSecurityContext': {
                'enabled': False
            },
            'service': {
                'type': 'ClusterIP'
            },
            'ingress': {
                'enabled': True,
                'hostname': 'www.test-org-app1.domain.com',
                'extraHosts': [],
                'path': '/',
            },
            'cloneStaticSiteFromGit': {
                'enabled': True,
                'repository': 'https://git.repo',
                'branch': 'master',
            },
            'aaa': 'bbb',
        },
    }
    assert component == expected
