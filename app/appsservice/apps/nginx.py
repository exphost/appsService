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

def prepare_values(spec):
    values_new = PREDEFINED_VALUES["values"].copy()
    values_new.update(spec.get("config", {}).get("raw_values", {}))
    values_new.update(spec.get("values", {}))
    return values_new


def prepare_chart(spec):
    chart_new = PREDEFINED_VALUES["chart"].copy()
    return chart_new
