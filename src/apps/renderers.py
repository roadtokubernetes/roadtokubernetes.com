from django.template.loader import render_to_string

from cfehome.utils import yaml_loader


def get_deployment_manifest(
    name="deployment", namespace="default", replicas=1, containers=[]
):
    data = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {"namespace": f"{namespace}", "name": name},
        "spec": {
            "replicas": replicas,
            "selector": {"matchLabels": {"app": name}},
            "template": {
                "metadata": {"labels": {"app": name}},
                "spec": {"containers": containers},
            },
        },
    }
    return yaml_loader.dump(data).strip()


def get_namespace_manifest(namespace="default"):
    data = {
        "apiVersion": "v1",
        "kind": "Namespace",
        "metadata": {"name": namespace},
    }
    return yaml_loader.dump(data).strip()


def get_service_manifest(
    name="service",
    namespace="default",
    deployment_name="deployment",
    service_type="ClusterIP",
    ports=[],
):
    data = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {"namespace": f"{namespace}", "name": name},
        "spec": {
            "type": service_type,
            "ports": ports,
            "selector": {"app": deployment_name},
        },
    }

    return yaml_loader.dump(data).strip()


def get_secrets_manifest(name="secret", namespace="default", data={}):
    _data = {
        "apiVersion": "v1",
        "kind": "Secret",
        "metadata": {"namespace": f"{namespace}", "name": name},
        "type": "Opaque",
        "data": data,
    }
    return yaml_loader.dump(_data).strip()


def get_certificate_issuer(
    name="cert-issuer-prod",
    private_secret_name="cert-issuer-secret",
    namespace="default",
    email="",
):
    _data = {
        "apiVersion": "cert-manager.io/v1",
        "kind": "Issuer",
        "metadata": {"name": name, "namespace": namespace},
        "spec": {
            "acme": {
                "server": "https://acme-v02.api.letsencrypt.org/directory",
                "email": email,
                "privateKeySecretRef": {"name": private_secret_name},
                "solvers": [{"http01": {"ingress": {"class": "nginx"}}}],
            }
        },
    }
    return yaml_loader.dump(_data).strip()


def get_ingress_manifest(
    domains=[],
    namespace="default",
    name="ingress",
    service_name="service",
    tls_secret_name=None,
    service_port=80,
    cert_issuer=None,
):
    ingress_doc = render_to_string("manifests/ingress-insecure.yaml")
    template_data = yaml_loader.load(ingress_doc)
    template_data["metadata"].update({"namespace": namespace, "name": name})
    if cert_issuer is not None:
        template_data["metadata"]["annotations"].update(
            {"cert-manager.io/issuer": cert_issuer}
        )
    hosts = [x for x in domains]
    ingress_rules = []
    spec = {}
    if len(domains) == 0:
        rule = {
            "http": {
                "paths": [
                    {
                        "backend": {
                            "service": {
                                "name": service_name,
                                "port": {"number": service_port},
                            }
                        },
                        "path": "/",
                        "pathType": "Prefix",
                    }
                ]
            },
        }
        ingress_rules.append(rule)
    else:
        for host in hosts:
            rule = {
                "host": host,
                "http": {
                    "paths": [
                        {
                            "backend": {
                                "service": {
                                    "name": service_name,
                                    "port": {"number": service_port},
                                }
                            },
                            "path": "/",
                            "pathType": "Prefix",
                        }
                    ]
                },
            }
            ingress_rules.append(rule)
        spec["tls"] = ({"hosts": hosts},)
    spec = {
        "rules": ingress_rules,
    }
    if tls_secret_name is not None:
        data = [{"secretName": tls_secret_name, "hosts": hosts}]
        spec["tls"] = data
    template_data["spec"] = spec
    return yaml_loader.dump(template_data).strip()
