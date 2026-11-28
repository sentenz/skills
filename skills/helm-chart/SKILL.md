---
name: helm-chart
description: Author, review, refactor, secure, test, and troubleshoot Helm charts for Kubernetes. Use for Chart.yaml, values overlays or schemas, Go templates and helpers, chart dependencies, release upgrades and rollbacks, Helm rendering failures, and GitOps-managed chart changes.
license: Apache-2.0
---

# Helm Chart

Start with the chart path, intended workload, Helm binary or controller, Kubernetes target, release name, namespace, and values files in precedence order. Recover these from the repository or deployment configuration. State any assumptions that affect the result.

1. **Establish the contract.** Inspect chart metadata, dependencies and locks, values and schema, template names, selectors, references, hooks, and existing CI. For an existing release, render the old revision first with the same inputs. Record identities as group, kind, namespace, and name.
2. **Choose the smallest change.** For authoring, copy the [application starter](assets/web/README.md) and retain only the required workload and options. For refactoring, preserve selectors, object names, values types, persistent claims, and hook timing. For a review, identify the file, triggering input, rendered effect, operational impact, and smallest verifiable correction for each finding.
3. **Load guidance for the decision at hand.**

   | Decision | Reference |
   | --- | --- |
   | Lifecycle, values, chart metadata, scope or template functions | [Fundamentals](references/fundamentals.md) |
   | Composition, names, ownership, hooks or GitOps | [Design patterns](references/patterns.md) |
   | Availability, upgrades, API compatibility or migrations | [Production operations](references/production.md) |
   | Identity, isolation, secrets or artifact verification | [Security](references/security.md) |
   | Render matrix, policy, CI or cluster acceptance | [Testing](references/testing.md) |
   | Failed render, install, rollout or rollback | [Troubleshooting](references/troubleshooting.md) |
   | Version-sensitive claim or platform prerequisite | [Primary sources](references/sources.md) |

4. **Exercise the actual change.** Validate the effective values and manifests for defaults, representative overlays, disabled features, and invalid input. Compare the baseline render for upgrades. Use [starter checks](scripts/check.py) for the bundled chart. Use an authorized disposable namespace for live tests.
5. **Report evidence.** Give the changed chart paths, release or compatibility consequences, exact test inputs and outcomes, and any remaining cluster-dependent checks. Distinguish template output, API acceptance, and observed controller behavior. For incidents, preserve the first failing stage and redact sensitive values before sharing evidence.
