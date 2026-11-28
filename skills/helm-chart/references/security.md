# Security decisions for chart authors

## Process identity and filesystem access

For Linux workloads targeting the Restricted Pod Security Standard, set Pod `runAsNonRoot: true` and an allowed seccomp profile such as `RuntimeDefault`. Set `allowPrivilegeEscalation: false` and drop `ALL` capabilities on each application, init and sidecar container. Review the complete standard for volume types, host namespaces, privileged mode and other controls. Verify against the namespace's enforced policy version and the image's actual user, ports and file permissions. Windows has OS-specific rules. [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)

Recommend a read-only root filesystem where the program supports it. Identify required writes, mount specific cache or temporary paths on appropriately sized writable volumes, then exercise startup and normal operations. A read-only root filesystem is additional hardening. Document the smallest exception when an application needs more access. [Security contexts](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/)

## API credentials and release records

- Derive workload permissions from API calls. Prefer a namespaced Role and RoleBinding with explicit verbs, resources and API groups. Document any required cross-namespace or cluster-wide operations. Keep installer's CRD permissions separate from runtime access. Let an operator supply an existing ServiceAccount when appropriate. [RBAC good practices](https://kubernetes.io/docs/concepts/security/rbac-good-practices/) · [Helm RBAC](https://helm.sh/docs/chart_best_practices/rbac/)
- For workloads without an API requirement, set Pod `automountServiceAccountToken: false`. Where identity is required, use an appropriately scoped projected token and check expiration, audience and application support. [Service accounts](https://kubernetes.io/docs/concepts/security/service-accounts/)
- Prefer a Secret reference with configurable name and keys. Keep credential values out of chart defaults, examples, command arguments, notes and test logs. Helm's default release storage uses Kubernetes Secrets and release records can include supplied values and rendered manifests. A rendered Secret remains sensitive even when its values are base64-encoded. Restrict access to release history, diagnostic artifacts and workload Secret mounts. Exercise credential rotation without printing its contents. [Helm storage backends](https://helm.sh/docs/topics/advanced/) · [Secret management](https://kubernetes.io/docs/concepts/security/secrets-good-practices/)

## Network reachability

An optional NetworkPolicy needs an enforcing network plugin. Identify traffic by source, destination, protocol and port. Include DNS and required upstream services when isolating egress. For each connection, check egress from the source Pod and ingress to the destination Pod. Policies are additive and apply to the Pods selected by each policy. Confirm allowed application flows and a representative denied connection in the target environment. [Kubernetes NetworkPolicy](https://kubernetes.io/docs/concepts/services-networking/network-policies/)

## Artifact identity

Use a known image repository and immutable digest for promoted releases. When supporting both tags and digests, document precedence and render-test the resulting reference. Pin test and hook images as well. A content digest identifies bytes. Publisher authentication additionally requires verification against a trusted signer or identity. With signed Helm packages and `.prov` files, use `helm verify` and a trusted keyring before promotion. Review the resolved dependencies and apply the organization's image verification policy to each shipped image. [Kubernetes images](https://kubernetes.io/docs/concepts/containers/images/) · [Helm provenance](https://helm.sh/docs/topics/provenance/) · [CNCF supply chain guidance](https://contribute.cncf.io/projects/best-practices/security/supply-chain/supply-chain-security-paper/)

For OCI distribution, log in using the registry's credential mechanism, package the reviewed chart and push the .tgz to an oci:// namespace. Helm derives the repository basename and tag from chart name and version. Record the registry manifest digest and promote the same artifact. Verify publisher identity under the registry's signing policy. When using classic Helm provenance, place the signed package's .prov next to it before pushing to include that layer. [Helm OCI registry workflow](https://helm.sh/docs/topics/registries/)
