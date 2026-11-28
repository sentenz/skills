#!/usr/bin/env python3
"""Render the bundled examples, assert cross-resource contracts, optionally validate schemas."""
import argparse
import re
import subprocess
import tempfile
from pathlib import Path

import yaml

ASSETS = Path(__file__).resolve().parents[1] / "assets"
CHART = ASSETS / "web"
ROUTE_API = "gateway.networking.k8s.io/v1/HTTPRoute"


def run(*args, stdin=None):
    proc = subprocess.run(args, input=stdin, text=True, capture_output=True)
    if proc.returncode:
        raise RuntimeError(f"{' '.join(map(str, args))}\n{proc.stdout}{proc.stderr}")
    return proc.stdout


def require(condition, message):
    if not condition:
        raise ValueError(message)


def inspect(objects, kind, extra_kinds, hooks):
    by_kind = {}
    for obj in objects:
        by_kind.setdefault(obj["kind"], []).append(obj)
    expected = {kind, "ServiceAccount", "ConfigMap", "NetworkPolicy"} | set(extra_kinds)
    if kind != "Job":
        expected.update(["Job", "Service"])
    require(set(by_kind) == expected, f"unexpected resources: {set(by_kind) ^ expected}")
    workload = by_kind[kind][0]
    template = workload["spec"]["template"]
    labels = template["metadata"]["labels"]
    name = workload["metadata"]["name"]
    require(by_kind["ServiceAccount"][0]["metadata"]["name"] == template["spec"]["serviceAccountName"], "unbound ServiceAccount")
    for svc in by_kind.get("Service", []):
        require(svc["spec"]["selector"] == labels, "Service selects incorrect Pods")
        require(svc["spec"]["ports"][0]["targetPort"] == template["spec"]["containers"][0]["ports"][0]["name"], "targetPort mismatch")
    require(by_kind["NetworkPolicy"][0]["spec"]["podSelector"]["matchLabels"] == labels, "policy selector mismatch")
    if kind != "Job":
        require(workload["spec"]["selector"]["matchLabels"] == labels, "controller selector mismatch")
        annotations = [j["metadata"]["annotations"]["helm.sh/hook"] for j in by_kind["Job"]]
        require(sorted(annotations) == sorted(hooks), "missing or unexpected hook")
    if kind == "StatefulSet":
        peers = [s["metadata"]["name"] for s in by_kind["Service"] if s["spec"].get("clusterIP") == "None"]
        require(workload["spec"]["serviceName"] in peers, "governing Service mismatch")
    if "HorizontalPodAutoscaler" in by_kind:
        hpa = by_kind["HorizontalPodAutoscaler"][0]["spec"]
        require("replicas" not in workload["spec"] and hpa["scaleTargetRef"]["name"] == name, "HPA ownership mismatch")
    if "PodDisruptionBudget" in by_kind:
        require(by_kind["PodDisruptionBudget"][0]["spec"]["selector"]["matchLabels"] == labels, "PDB selector mismatch")
    if "Role" in by_kind:
        rule = by_kind["Role"][0]["rules"][0]
        require(rule == dict(apiGroups=[""], resources=["configmaps"], resourceNames=[name], verbs=["get"]), "excess RBAC")
    if "Ingress" in by_kind:
        backend = by_kind["Ingress"][0]["spec"]["rules"][0]["http"]["paths"][0]["backend"]["service"]
        require(backend == dict(name=name, port={"name": "http"}), "Ingress backend mismatch")
    if "HTTPRoute" in by_kind:
        backend = by_kind["HTTPRoute"][0]["spec"]["rules"][0]["backendRefs"][0]
        require(backend == dict(name=name, port=80), "HTTPRoute backend mismatch")
    for obj in objects:
        if obj["kind"] not in {"Deployment", "StatefulSet", "DaemonSet", "Job"}:
            continue
        pod = obj["spec"]["template"]["spec"]
        require(pod["securityContext"]["runAsNonRoot"] and pod["securityContext"]["seccompProfile"]["type"] == "RuntimeDefault", "pod security")
        require(pod["automountServiceAccountToken"] == ("Role" in by_kind and obj is workload), "unexpected token policy")
        for container in pod["containers"]:
            ctx = container["securityContext"]
            require(not ctx["allowPrivilegeEscalation"] and ctx["readOnlyRootFilesystem"] and ctx["capabilities"]["drop"] == ["ALL"], "container security")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--helm", default="helm")
    parser.add_argument("--kube-version", default="1.36.0")
    parser.add_argument("--kubeconform", help="validate every render with this executable")
    parser.add_argument("--schema-location", action="append", default=[], help="repeat for built-ins and the HTTPRoute schema")
    args = parser.parse_args()
    version = ["--kube-version", args.kube_version]
    def overlay(name):
        return ["-f", ASSETS / "examples" / (name + ".yaml")]
    cases = [
        ("default", "Deployment", [], [], ["test"]),
        ("ha", "Deployment", overlay("ha"), ["HorizontalPodAutoscaler", "PodDisruptionBudget"], ["test"]),
        ("gateway", "Deployment", overlay("gateway") + ["--api-versions", ROUTE_API], ["HTTPRoute"], ["test"]),
        ("ingress", "Deployment", overlay("ingress"), ["Ingress"], ["test"]),
        ("stateful", "StatefulSet", overlay("stateful"), [], ["test"]),
        ("daemon", "DaemonSet", ["--set", "workload=DaemonSet"], [], ["test"]),
        ("batch", "Job", ["--set", "workload=Job"], [], []),
        ("identity", "Deployment", ["--set", "configReader=true,existingSecret=external,smokeHook=true"], ["Role", "RoleBinding"], ["test", "post-install,post-upgrade"]),
    ]
    with tempfile.TemporaryDirectory() as cache:
        count = 0
        for label, kind, options, extra, hooks in cases:
            cmd = [args.helm, "template", "demo", CHART, "-n", "qa", *version, *options]
            rendered = run(*cmd)
            require(rendered == run(*cmd), f"{label}: unstable render")
            objects = [doc for doc in yaml.safe_load_all(rendered) if doc]
            inspect(objects, kind, extra, hooks)
            if label == "identity":
                volumes = next(obj for obj in objects if obj["kind"] == kind)["spec"]["template"]["spec"]["volumes"]
                require(any(v.get("secret", {}).get("secretName") == "external" for v in volumes), "missing Secret reference")
            if args.kubeconform:
                flags = [flag for path in args.schema_location for flag in ("-schema-location", path)]
                run(args.kubeconform, "-strict", "-kubernetes-version", args.kube_version, "-cache", cache, *flags, stdin=rendered)
            count += len(objects)
    run(args.helm, "lint", CHART, "--strict", *version)
    names = set()
    for release in ("1demo", "test.example", "test-example", "a" * 53):
        docs = list(yaml.safe_load_all(run(args.helm, "template", release, CHART, *version)))
        for doc in filter(None, docs):
            name = doc["metadata"]["name"]
            require(len(name) <= 63 and re.fullmatch(r"[a-z][a-z0-9-]*[a-z0-9]", name), f"invalid DNS label {name}")
        service = next(d for d in docs if d and d["kind"] == "Service")
        require(service["metadata"]["name"] not in names, "release name collision")
        names.add(service["metadata"]["name"])
    bad = [
        (["--set", "replicas=0"], "replicas"),
        (["--set", "unknown=true"], "unknown"),
        (["--set", "workload=Job,autoscaling.enabled=true"], "autoscaling"),
        (["--set", "route.mode=ingress"], "route"),
        (["--set", "image=busybox:latest"], "image"),
        (["--set", "autoscaling.enabled=true,autoscaling.min=9"], "autoscaling.min exceeds"),
        (overlay("gateway"), "gateway mode requires"),
    ]
    for options, expected in bad:
        proc = subprocess.run([args.helm, "template", "demo", CHART, *version, *options], text=True, capture_output=True)
        require(proc.returncode and expected in proc.stderr, f"expected rejection containing {expected!r}: {proc.stderr}")
    print(f"{args.kube_version}: strict lint, {len(cases)} deterministic renders ({count} resources), {len(bad)} expected rejections passed")


if __name__ == "__main__":
    main()
