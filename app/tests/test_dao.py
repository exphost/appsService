import pytest


def test_list_apps(app):
    apps = app.dao.list_apps(org="test-org")
    assert len(apps) == 2
    assert set(apps) == set(["app1", "app2"])


def test_list_apps_empty_org(app):
    apps = app.dao.list_apps(org="test-org3")
    assert len(apps) == 0


def test_get_app(app):
    components = app.dao.get_app(org="test-org", app="app1")
    assert len(components) == 2
    assert components[0]["name"] == "generic-app"
    assert components[0]["repo"] == "https://gitlab.exphost.pl/charts"
    assert components[0]["version"] == "v0.0.0-3-ge9ad446"
    assert components[0]["releaseName"] == "frontend"
    inline = components[0]["valuesInline"]
    assert inline["image"]["repository"] == "registry.gitlab.exphost.pl/onelink/onelink-frontend" # noqa
    assert inline["image"]["tag"] == "v0.0.1"
    assert inline["_type"] == "react"
    assert components[1]["name"] == "generic-app"
    assert components[1]["repo"] == "https://gitlab.exphost.pl/charts"
    assert components[1]["version"] == "v0.0.0-3-ge9ad446"
    assert components[1]["releaseName"] == "app2"
    assert components[1]["valuesInline"]["_type"] == "asd"


def test_get_app_with_updates(app):

    components = app.dao.get_app(org="test-org", app="app1")
    assert len(components) == 2
    assert components[0]["name"] == "generic-app"
    assert components[0]["repo"] == "https://gitlab.exphost.pl/charts"
    assert components[0]["version"] == "v0.0.0-3-ge9ad446"
    assert components[0]["releaseName"] == "frontend"
    inline = components[0]["valuesInline"]
    assert inline["image"]["repository"] == "registry.gitlab.exphost.pl/onelink/onelink-frontend" # noqa
    assert inline["image"]["tag"] == "v0.0.1"
    assert inline["_type"] == "react"
    assert components[1]["name"] == "generic-app"
    assert components[1]["repo"] == "https://gitlab.exphost.pl/charts"
    assert components[1]["version"] == "v0.0.0-3-ge9ad446"
    assert components[1]["releaseName"] == "app2"
    assert components[1]["valuesInline"]["_type"] == "asd"


def test_app_not_found(app):
    with pytest.raises(FileNotFoundError):
        app.dao.get_app(org="test-org", app="app4")


def test_add_app(app):
    app.dao.save_app(org="test-org", app="app4", components=[
        {
            "name": "nginx",
            "releaseName": "frontend",
            "repo": "repo4",
            "version": "1.1.0",
            "valuesInline": {
                "_type": "nginx"
            }
        }
    ])
    components = app.dao.get_app(org="test-org", app="app4")
    assert len(components) == 1
    assert components[0]["name"] == "nginx"
    assert components[0]["repo"] == "repo4"
    assert components[0]["version"] == "1.1.0"
    assert components[0]["releaseName"] == "frontend"
    assert components[0]["valuesInline"]["_type"] == "nginx"


def test_update_app(app):
    app.dao.save_app(org="test-org3", app="app1", components=[
        {
            "name": "nginx",
            "releaseName": "frontend",
            "repo": "repo4",
            "version": "1.1.0",
            "valuesInline": {
                "_type": "nginx"
            }
        },
        {
            "name": "flask",
            "releaseName": "backend",
            "repo": "repo42",
            "version": "2.1.0",
            "valuesInline": {
                "_type": "flask"
            }
        }
    ])
    app.dao.save_app(org="test-org3", app="app1", components=[
        {
            "name": "nginx",
            "releaseName": "frontend",
            "repo": "repo5",
            "version": "1.2.0",
            "valuesInline": {
                "_type": "nginx"
            }
        }
    ])
    components = app.dao.get_app(org="test-org3", app="app1")
    assert len(components) == 1
    assert components[0]["name"] == "nginx"
    assert components[0]["repo"] == "repo5"
    assert components[0]["version"] == "1.2.0"
    assert components[0]["releaseName"] == "frontend"
    assert components[0]["valuesInline"]["_type"] == "nginx"


def test_add_component(app):
    app.dao.save_app(org="test-org3", app="app1", components=[
        {
            "name": "nginx",
            "releaseName": "frontend",
            "repo": "repo4",
            "version": "1.1.0",
            "valuesInline": {
                "_type": "nginx"
            }
        },
        {
            "name": "flask",
            "releaseName": "backend",
            "repo": "repo42",
            "version": "2.1.0",
            "valuesInline": {
                "_type": "flask"
            }
        }
    ])
    app.dao.update_component(org="test-org3", app="app1", component={
        "name": "nginx",
        "releaseName": "frontend",
        "repo": "repo5",
        "version": "1.2.0",
        "valuesInline": {
            "_type": "nginx"
        }
    })
    components = app.dao.get_app(org="test-org3", app="app1")
    assert len(components) == 2
    assert components[0]["name"] == "nginx"
    assert components[0]["repo"] == "repo5"
    assert components[0]["version"] == "1.2.0"
    assert components[0]["releaseName"] == "frontend"
    assert components[0]["valuesInline"]["_type"] == "nginx"
    assert components[1]["name"] == "flask"
    assert components[1]["repo"] == "repo42"
    assert components[1]["version"] == "2.1.0"
    assert components[1]["releaseName"] == "backend"


def test_delete_component(app):
    app.dao.save_app(org="test-org3", app="app1", components=[
        {
            "name": "nginx",
            "releaseName": "frontend",
            "repo": "repo4",
            "version": "1.1.0",
            "valuesInline": {
                "_type": "nginx"
            }
        },
        {
            "name": "flask",
            "releaseName": "backend",
            "repo": "repo42",
            "version": "2.1.0",
            "valuesInline": {
                "_type": "flask"
            }
        }
    ])
    app.dao.delete_component(org="test-org3", app="app1", component="backend")
    components = app.dao.get_app(org="test-org3", app="app1")
    assert len(components) == 1
    assert components[0]["name"] == "nginx"
    assert components[0]["repo"] == "repo4"
    assert components[0]["version"] == "1.1.0"
    assert components[0]["releaseName"] == "frontend"
    assert components[0]["valuesInline"]["_type"] == "nginx"


def test_update_component_non_existing_app(app):
    with pytest.raises(FileNotFoundError):
        app.dao.update_component(org="test-org3", app="app5", component={
            "name": "nginx",
            "releaseName": "frontend",
        })


def test_delete_component_non_existing_app(app):
    with pytest.raises(FileNotFoundError):
        app.dao.delete_component(
            org="test-org3",
            app="app5",
            component="backend")


def test_get_component(app):
    component = app.dao.get_component(
        org="test-org",
        app="app1",
        component="app2")
    assert component["releaseName"] == "app2"
    assert component["repo"] == "https://gitlab.exphost.pl/charts"
    assert component["version"] == "v0.0.0-3-ge9ad446"


def test_get_component_non_existing(app):
    with pytest.raises(FileNotFoundError):
        app.dao.get_component(org="test-org", app="app1", component="app3")
