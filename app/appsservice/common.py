import os
import jinja2


def create_project_if_needed(subpath, org, repo, gitdir):
    ingit_project_path = os.path.join(
        subpath,
        org,
        "project.yml"
    )
    project_path = os.path.join(
        gitdir,
        ingit_project_path
    )

    if not os.path.exists(project_path):
        with open("appsservice/templates/appproject.yml.j2", "r") as file:
            template = jinja2.Template(file.read())
        project = template.render(name=org,
                                  namespace="tenant-"+org)
        with open(project_path, "w") as file:
            file.write(project)
        repo.index.add(ingit_project_path)
