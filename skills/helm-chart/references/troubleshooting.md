# Find the first failing boundary

Preserve the chart and dependency revisions, release coordinates, client/controller version, ordered overlays and first error. Reproduce with synthetic credentials. Debug renders, Helm values, events, and container logs can expose private material; retain locally and redact before sharing.

| Symptom | Evidence to collect | Smallest next action |
| --- | --- | --- |
| Missing chart or helper | Compare Chart.yaml, Chart.lock, charts/ and helm dependency list. Inspect the helper name and context. | Build from the committed lock, restore the vendored chart or registry credentials, then render again. |
| Schema failure, nil pointer, unexpected type | Render with the same ordered files and --set types. Narrow to the last overlay that changes the outcome. | Correct the input or add a conditional schema rule. Ensure defaults support the disabled path. |
| YAML parse error or wrong scalar | Render with --debug locally and --show-only templates/FILE when possible. Compare indentation, trim markers and quoted fields. | Separate document boundaries, use nindent, preserve numeric types; rerun the full chart. |
| No match for kind | Compare apiVersion/kind with kubectl api-resources and CRD Established condition. Local synthetic capabilities only affect rendering. | Select a served API or arrange CRD/controller installation with its owner. |
| Already exists or immutable field | Compare live object's release metadata, rendered identity, old revision and new selectors or claims. | Preserve the old identity for a refactor; plan adoption or replacement explicitly for a migration. |
| Upgrade waits or fails on a hook | Inspect helm status/history, hook Job conditions, Pod events and logs, and namespace quota. | Repair the exact failing dependency. Check whether a retry repeats an external migration or side effect. |
| Pods Pending or crash-looping | Classify scheduler, image pull, PVC binding, permission, OOM, config key and probe failures using events and previous logs. | Change the smallest serving or capacity contract and rerun readiness and termination checks. |
| Service has no endpoints or a route returns 503 | Compare selector to Pod labels and readiness, EndpointSlices and named ports. Check HTTPRoute Accepted/ResolvedRefs, Ingress class, policies and DNS. | Correct the broken link, then probe from an allowed client in the target namespace. |
| HPA unknown or drain blocked | Inspect HPA conditions, metrics API and CPU requests; inspect PDB disruptionsAllowed, desired healthy count and available replicas. | Restore metrics or capacity and check actual disruption tolerance before changing budgets. |
| Desired state reverts | Inspect reconciler events, chart/values revision and managedFields. | Fix the source of truth, reconcile once, and compare rendered, admitted and observed state. |
