# import threading
import git
import os
import yaml
import time
import threading


class AppsDao(object):
    def __init__(self, gitrepo, subpath=None):
        self.last_update = 0
        self.gitsem = threading.Semaphore()
        self.gitdir = "workdir"
        ssh_cmd = (
            "ssh "
            "-o StrictHostKeyChecking=no "
            "-o UserKnownHostsFile=/dev/null "
            "-i /app/sshkey/id_rsa"
        )
        self.repo = git.Repo.clone_from(
            gitrepo,
            self.gitdir,
            env=dict(GIT_SSH_COMMAND=ssh_cmd)
        )

    def _app_path(self, org, app):
        return os.path.join(
            self._app_dir(org, app),
            "base",
            "kustomization.yml"
        )

    def _app_dir(self, org, app):
        return os.path.join(
            self.gitdir,
            org,
            app
        )

    def _ingit_app_dir(self, org, app):
        return os.path.join(
            org,
            app
        )

    def _is_app(self, org, app):
        return os.path.exists(self._app_path(org, app))

    def git_update(self, force=False):
        self.gitsem.acquire()
        if time.time() - self.last_update > 60 or force:
            self.repo.remote().pull()
            self.last_update = time.time()
        self.gitsem.release()

    def list_apps(self, org):
        self.git_update()
        org_dir = os.path.join(self.gitdir, org)
        if not os.path.exists(org_dir):
            return []
        return [i for i in next(os.walk(org_dir))[1] if self._is_app(org, i)]

    def get_app(self, org, app):
        if not self._is_app(org, app):
            raise FileNotFoundError
        self.git_update()
        obj = None
        with open(self._app_path(org, app)) as f:
            obj = yaml.safe_load(f.read())
        return obj.get("helmCharts", None)

    def get_app_namespace(self, org, app):
        if not self._is_app(org, app):
            raise FileNotFoundError
        self.git_update()
        obj = None
        with open(self._app_path(org, app)) as f:
            obj = yaml.safe_load(f.read())
        return obj.get("namespace", None)

    def save_app(self, org, app, components):
        self.git_update(force=True)
        self.gitsem.acquire()
        if not os.path.exists(self._app_dir(org, app) + "/base"):
            os.makedirs(self._app_dir(org, app) + "/base", exist_ok=True)
        if not os.path.exists(self._app_path(org, app)):
            namespace = "tenant-" + org
            with open(self._app_path(org, app), "w") as f:
                f.write(f"namespace: {namespace}")
        data = None
        with open(self._app_path(org, app)) as f:
            data = yaml.safe_load(f.read())
        data["helmCharts"] = components
        with open(self._app_path(org, app), "w") as f:
            f.write(yaml.dump(data, default_flow_style=False))

        self.repo.index.add(self._ingit_app_dir(org, app))
        self.repo.index.commit("update app")
        self.repo.remotes.origin.push()
        self.gitsem.release()
        return True

    def update_component(self, org, app, component):
        if not self._is_app(org, app):
            raise FileNotFoundError
        components = self.get_app(org, app)
        found = False
        for i in range(len(components)):
            if components[i]["releaseName"] == component["releaseName"]:
                components[i] = component
                found = True
        if not found:
            components.append(component)
        return self.save_app(org, app, components)

    def delete_component(self, org, app, component):
        if not self._is_app(org, app):
            raise FileNotFoundError
        components = self.get_app(org, app)
        for i in range(len(components)):
            if components[i]["releaseName"] == component:
                del components[i]
        self.save_app(org, app, components)

    def get_component(self, org, app, component):
        if not self._is_app(org, app):
            raise FileNotFoundError
        components = self.get_app(org, app)
        for i in range(len(components)):
            if components[i]["releaseName"] == component:
                return components[i]
        raise FileNotFoundError
