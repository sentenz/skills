# Web workload starter

The default release serves a ConfigMap as a static page on port 8080 behind a ClusterIP Service. The image is a multi-platform BusyBox 1.37.0 digest. Its applets supply the HTTP server, batch command, and smoke client. Replace the commands, probes, and test image together when adopting a different image. Adapt resource budgets from measurements.

Use Helm 3 or 4 with an API-compatible client and cluster. This example declares stable Kubernetes 1.34 through 1.37 targets. Select a maintained patch and check the client's version-skew policy. The identity library is vendored so dependency builds require no registry. Execute from the directory containing this README.

```sh
helm dependency build .
helm lint . --strict --kube-version 1.36.0
helm template demo . --namespace sandbox --kube-version 1.36.0
helm template demo . -f ../examples/ha.yaml --kube-version 1.36.0
helm template demo . -f ../examples/gateway.yaml --kube-version 1.36.0 \
  --api-versions gateway.networking.k8s.io/v1/HTTPRoute
```

| Input | Effect and prerequisites |
| --- | --- |
| `workload`, `replicas` | Choose Deployment, StatefulSet, DaemonSet, or Job on a fresh release. Changing controller kind is a migration. Jobs validate the mounted page and terminate. DaemonSets run on eligible nodes. |
| `image`, `page`, `resources`, `graceSeconds` | Supply a digest, public page text, CPU/memory requests and limits, and time for termination. The page checksum drives rollouts. |
| `storageSize` | StatefulSet creates a headless governing Service and one ReadWriteOnce claim per ordinal. Provide a default StorageClass or prebound storage. Plan retention, backup and resizing separately. |
| `autoscaling`, `disruptionBudget` | The HA overlay enables CPU scaling on Deployments and allows one voluntary disruption. Supply a metrics API and distribute replicas across failure domains. |
| `networkPolicy` | With an enforcing CNI, server pods accept traffic on 8080 from same-release client pods in the namespace. Server egress is isolated. Extra namespace labels admit all pods in matching namespaces. Constrain pod peers further when those namespaces are shared. |
| `route` | Ingress needs a class, DNS, and a TLS Secret. HTTPRoute needs the v1 CRD and a same-namespace Gateway with a suitable listener, TLS and controller. Verify actual data-plane source labels against the example ingress rule. |
| `existingSecret`, `configReader` | Supply an existing Secret name to mount its contents; customize projected keys for real applications. The optional token and Role grant only get on the release ConfigMap. Add narrowly scoped API egress for a real API client. |
| `smokeHook` | Optional post-install/post-upgrade connectivity check. The same check is available on demand with helm test. Probe Jobs require DNS and egress to the Service under ambient namespace policies. |

Each release owns its namespaced objects. The fixed selector name and release label are part of the upgrade contract. Replacing a completed standalone Job's Pod template requires a new identity or an explicit replacement procedure. A rollback of the release cannot restore data on its PVCs.

In a disposable namespace, install with `--wait`, run `helm test`, change the page in an upgrade, and check both the response and the previous revision after rollback. Inspect packaged contents with `helm package .` and `tar -tzf web-0.1.0.tgz` before distribution. Run the skill's checks on the original starter before adapting its contract.
