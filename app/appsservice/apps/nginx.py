PREDEFINED_VALUES = {
    "chart": {
        "name": "nginx",
        "repository": "https://charts.bitnami.com/bitnami",
        "version": "15.10.3",
    },
    "values": {
        "containerSecurityContext": {
            "enabled": False
        },
        "service": {
            "type": "ClusterIP"
        },
    },
}


def prepare_values(spec, app):
    def add_domain(hostname):
        return f'{hostname}.{app["spec"].get("config",{}).get("domain", "unset")}'  # noqa E501
    values_new = PREDEFINED_VALUES["values"].copy()
    values_new.update(spec.get("config", {}).get("raw_values", {}))
    config = spec.get("config", {})
    if config.get("hostnames", None):
        values_new["ingress"] = {
            "enabled": True,
            "hostname": add_domain(config["hostnames"][0]),
            "path": "/",
            "extraHosts": list(map(add_domain, config["hostnames"][1:])),
        }
    if config.get("git", None):
        git = config["git"]
        if git.get("repo", None):
            values_new["cloneStaticSiteFromGit"] = {
                "enabled": True,
                "repository": git["repo"],
                "branch": git.get("branch", "master"),
            }
    values_new.update(spec.get("values", {}))
    return values_new


def prepare_chart(spec):
    chart_new = PREDEFINED_VALUES["chart"].copy()
    return chart_new
