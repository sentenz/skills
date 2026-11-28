# Release evidence

Use a pinned Helm client and declare the target server version explicitly in offline checks. Keep synthetic fixtures for credentials. Record command, version, release, namespace, ordered values, expected behavior, and result.

1. **Resolve and lint.** Confirm Chart.lock exists for a chart with resolved dependencies and inspect vendored sources. Run `helm dependency build CHART` then `helm lint CHART --strict --kube-version 1.36.0 -f VALUES`. Helm validates the schema against merged values. Exercise missing required fields, rejected types, conflicting modes, lower and upper version bounds and subchart values. A template fail in lint mode may only log information; assert a nonzero exit from an actual negative render.
2. **Render and assert.** Render twice with identical release coordinates and compare parsed resources (use byte equality for deterministic fixtures). Exercise each workload, supported Kubernetes minor, ordered overlays, hook enablement, and upgrade-only branches with --is-upgrade. Assert selectors select the intended pods, targetPorts resolve, the HPA owns replicas, and every Secret reference and binding points to the intended name. Assert absence of disabled resources. Capture the old/new identity and field diff.
3. **Validate manifests.** Use kubeconform -strict with the target minor and pinned schema locations, including the installed versions of all CRDs. Missing schemas should fail CI. The starter check below always renders HTTPRoute with explicit discovery. Supply its v1 JSON schema from the target Gateway API CRD's spec.versions entry. Built-in schemas alone cannot validate it. Code the organization's admission rules as policy tests, then check real API admission with server-side dry-run on the target API versions.
4. **Test the release.** In an isolated cluster or namespace with authorized credentials, install a known predecessor, wait for readiness, run Helm tests, upgrade the same release, verify application behavior and rollback. Check hook cleanup, persisted data and an independent client request. A first-version starter may vary a value to exercise revision history; also test chart-to-chart migrations when a predecessor exists.
5. **Match delivery.** In PR CI, exercise minimum/maximum supported versions, packaged chart contents and dependency locks. Run the same release once through the production GitOps renderer and reconcile it twice. Capture drift, admission mutations, route conditions, SLO checks and a negative policy test before promotion.

## Starter unit checks

From the skill root, install Python 3 and PyYAML and put Helm on PATH, or pass --helm. The script validates eight positive configurations and seven rejection paths. Add schema locations for the target Kubernetes and Gateway API versions.

```sh
python3 scripts/check.py --helm helm --kube-version 1.36.0
python3 scripts/check.py --helm helm --kube-version 1.36.0 --kubeconform kubeconform \
  --schema-location 'schemas/{{.NormalizedKubernetesVersion}}-standalone-strict/{{.ResourceKind}}{{.KindSuffix}}.json' \
  --schema-location 'schemas/{{.Group}}/{{.ResourceKind}}_{{.ResourceAPIVersion}}.json'
```

## Disposable integration run

Run with a dedicated kubecontext and an existing test namespace. Set NS, CHART, PRIOR and VALUES to the test namespace, candidate, predecessor and a compatible overlay. The namespace needs the target admission policy, image access and the chart prerequisites.

```sh
helm install smoke "$PRIOR" -n "$NS" -f "$VALUES" --wait --timeout 5m
helm test smoke -n "$NS" --timeout 2m
helm upgrade smoke "$CHART" -n "$NS" -f "$VALUES" --wait --timeout 5m
helm test smoke -n "$NS" --timeout 2m
helm history smoke -n "$NS"
helm rollback smoke 1 -n "$NS" --wait --timeout 5m
helm test smoke -n "$NS" --timeout 2m
helm uninstall smoke -n "$NS"
```

Revision 1 here is the known healthy install in a newly created release. Check credentials, service reachability and PVC contents after each transition. Record whether tests exercised only schema/identity, the API server, or actual workloads on nodes.
