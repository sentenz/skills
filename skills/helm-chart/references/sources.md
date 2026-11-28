# Upstream references

Consult the documentation for the deployed client or controller version. A chart format, a Helm binary and a Kubernetes API server have distinct compatibility contracts.

| Design question | Primary sources |
| --- | --- |
| What may a chart contain, and how are values merged and validated? | [Helm chart specification](https://helm.sh/docs/topics/charts/) and [chart best practices](https://helm.sh/docs/chart_best_practices/) |
| Can this Helm client target this cluster? Which behaviors changed in Helm 4? | [Helm 3 skew table](https://helm.sh/docs/v3/topics/version_skew/), [Helm 4 skew table](https://helm.sh/docs/topics/version_skew/) and [Helm 4 migration overview](https://helm.sh/docs/overview/) |
| Which dependency versions enter a build? How is the artifact verified? | [Dependency build](https://helm.sh/docs/helm/helm_dependency_build/), [OCI registries](https://helm.sh/docs/topics/registries/) and [provenance](https://helm.sh/docs/topics/provenance/) |
| What does each validation step exercise? | [Template debugging](https://helm.sh/docs/chart_template_guide/debugging/), [chart tests](https://helm.sh/docs/topics/chart_tests/), [Kubeconform schema sources and limitations](https://github.com/yannh/kubeconform) and [chart-testing](https://github.com/helm/chart-testing) |
| Can an existing release upgrade or roll back? | [Helm 3 upgrade](https://helm.sh/docs/v3/helm/helm_upgrade/), [Helm 4 upgrade](https://helm.sh/docs/helm/helm_upgrade/), [Helm rollback](https://helm.sh/docs/helm/helm_rollback/), [removed Kubernetes APIs](https://helm.sh/docs/topics/kubernetes_apis/) and [field ownership](https://kubernetes.io/docs/reference/using-api/server-side-apply/) |
| Who owns CRD registration, stored data and hooks? | [Helm CRDs](https://helm.sh/docs/chart_best_practices/custom_resource_definitions/), [Kubernetes CRD versioning](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definition-versioning/) and [Helm hook lifecycle](https://helm.sh/docs/topics/charts_hooks/) |
| Who reconciles a GitOps release? | [OpenGitOps principles](https://opengitops.dev/), [Argo CD Helm integration](https://argo-cd.readthedocs.io/en/stable/user-guide/helm/) and [Flux HelmRelease](https://fluxcd.io/flux/components/helm/helmreleases/) |
| Which security controls are Kubernetes policy and which are release practices? | [Kubernetes Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/), [RBAC guidance](https://kubernetes.io/docs/concepts/security/rbac-good-practices/) and [CNCF supply chain security guidance](https://contribute.cncf.io/projects/best-practices/security/supply-chain/supply-chain-security-paper/) |

For workload, networking and security decisions, [production](production.md) and [security](security.md) link the relevant upstream specifications alongside their application.

The chart format, schema constraints, Kubernetes field semantics and enforced admission policies define requirements. The starter's version window, resource sizes, chart decomposition and opt-in features are design choices. Evaluate those against the target platform. Review public contract changes against [Semantic Versioning](https://semver.org/spec/v2.0.0.html), values validation against [JSON Schema Draft 7](https://json-schema.org/draft-07), and distribution against the [Agent Skills specification](https://agentskills.io/specification).
