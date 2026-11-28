# Composition and release design

| Situation | Pattern and consequence |
| --- | --- |
| Several templates repeat identity | Prefix helper names with chart and contract version. Named templates share a namespace across dependencies. Pass an explicit root or a documented dict. Use stable application, release and component labels for selectors. Keep version and managed-by outside immutable selectors. |
| Several charts share code | Put named helpers in a type-library dependency. It cannot be installed as an application. Vendor the reviewed source or lock the exact artifact. The starter's vendored identity helper accepts an explicit release context. |
| A coordinated application needs several services | Use an umbrella chart only when components share ownership and release cadence. Pin dependencies in Chart.yaml, commit Chart.lock and run helm dependency build in CI. Use dependency update for intentional resolution. A lock identifies dependency choices, so also verify retrieved artifacts. |
| Environments differ | Keep one chart and small ordered overlays for differences. Give each dependency its own values map and use global only for genuinely shared settings. Render every supported combination including false, zero and empty values where valid. |
| Optional resource | Put the condition around the complete document. Validate required inputs when enabled. Choose an explicit failure if a requested API is absent. Validate every referencing resource and Service target when toggling an option. |
| Independent tenants | Use separate releases and namespace-scoped RBAC. Put shared Gateways, classes, CRDs, namespace policies and cluster roles under identified platform ownership. Namespace separation also needs admission, network and secret access controls. |
| Controller-managed release | Pin chart, dependencies, values and image by immutable revision where available. Random values, clocks, generated credentials and lookup introduce render drift. Set a single owner per field and object. Keep replicas out of an HPA-managed manifest after a planned ownership handoff. |

## Hooks and rollout

A pre-upgrade hook runs before the target manifests are updated. An application migration may therefore see old credentials, schemas, and binaries. Use a separately scoped, idempotent Job with a bounded deadline, explicit ordering where needed, a retry-safe migration lock, and a cleanup policy. Decide whether to keep failures for diagnosis. Helm does not manage hooks like ordinary release resources. A post-upgrade smoke failure can fail an otherwise healthy release. Verify hook semantics under the actual GitOps controller.

For a rolling Deployment, size surge and unavailable counts against quotas, readiness time and capacity. Use traffic-weighted or blue/green adoption only with a controller that supports the chosen routing contract. Give both versions distinct selectors, coordinate traffic cutover, and retain a rollback window. With persistent state, expand the schema for both versions before switching traffic, then contract in a later release.

For a port migration, inventory the published Service port, targetPort, Pod port names and actual listeners. During a rolling upgrade a common named target can resolve to different numbers on old and new Pods. If the old Pods have no port name, introduce it on their current working port first, switch the Service to that name after all serving Pods advertise it, then move the new listener and probes. Verify EndpointSlices and requests while both revisions serve. [Service port definitions](https://kubernetes.io/docs/concepts/services-networking/service/#port-definitions)
