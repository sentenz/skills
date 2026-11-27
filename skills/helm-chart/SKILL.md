---
name: helm-chart
description: Create, modify, review, and troubleshoot Kubernetes Helm charts. Use for Chart.yaml, values.yaml, values.schema.json, Go templates under templates/, chart dependencies and locks, helm lint or helm template failures, and changes that could break an existing release during an upgrade.
---

# Helm Chart

## Establish the chart contract

Locate the chart root by its `Chart.yaml`. Inspect adjacent charts, values files, CI commands, and the Helm and Kubernetes versions the project supports. Identify the release name, namespace, and ordered overrides used to reproduce the request. Later `-f` files override earlier ones. Use synthetic values for credentials.

For a new application chart, start from the workload's image, ports, configuration, and storage requirements. Create a v2 `Chart.yaml` with a chart name and SemVer `version`, a `values.yaml`, and templates for the requested resources. Quote `appVersion` when supplied. Chart `version` identifies the package and changes according to the project's release policy. For a library chart, exercise its helpers through a consuming application chart.

For an existing chart, first render the current revision with representative inputs. Retain that output for comparison. For a review, trace each finding from a chart path or values key to its effect on a rendered Kubernetes object.

## Implement the change

- Treat values keys, their types, and their defaults as a public interface. Set static defaults in `values.yaml`. Helm's `default` treats `false` and `0` as empty, so render those fields directly when they are valid overrides. Keep any `values.schema.json` and documented examples in sync.
- Define shared names and labels in chart-prefixed helpers such as `api.selectorLabels` in `templates/_helpers.tpl`. Deployment selectors must match Pod template labels and remain stable across upgrades. Keep version labels outside selectors. Check that Service selectors identify the intended Pods and that named target ports exist.
- Use `include` or `toYaml` with `nindent` for nested blocks. Inside `range` and `with`, pass the intended context explicitly to helpers. Quote string fields such as environment variable values and preserve numeric and boolean types where the Kubernetes API expects them.
- If the chart declares dependencies, check the project's vendoring convention. Rebuild missing dependencies with `helm dependency build "$chart"` when a lock is present. Use `helm dependency update "$chart"` for intentional resolution changes and review the resulting lock. Without a lock, build can resolve new versions.

## Verify the rendered behavior

Set the shell variables below to the actual chart path and a representative, non-secret override file. Keep the release name and namespace consistent between comparisons.

```sh
chart=./charts/api
overrides=./ci/staging-values.yaml
helm lint "$chart"
helm template sample "$chart" --namespace staging
helm lint "$chart" -f "$overrides"
helm template sample "$chart" --namespace staging -f "$overrides"
```

Inspect the affected resources in both renders. For a conditional resource, exercise enabled and disabled cases. For a schema constraint, try one invalid value and verify that Helm rejects it for the expected reason. If rendering fails, isolate the smallest failing override, then use `--debug` and, when useful, `--show-only` with the template path. Debug output can contain Secret data.

For upgrades, render the base and candidate with identical release inputs, including an existing consumer's values. Compare resource names, Deployment selectors, Service routing, and PVC identity or storage changes. If templates branch on `.Release.IsUpgrade`, also render the candidate with `--is-upgrade`. Local rendering cannot establish cluster admission, CRD availability, or workload readiness. Report which checks ran and which require a cluster. Keep chart authoring and review local unless deployment is requested.

Return the chart changes or review findings, the values combinations exercised, and the observable result. Call out any migration required for existing releases.

## References

- [Helm chart format](https://helm.sh/docs/topics/charts/)
- [Chart template best practices](https://helm.sh/docs/chart_best_practices/templates/)
- [Dependency build behavior](https://helm.sh/docs/helm/helm_dependency_build/)
- [Local rendering options](https://helm.sh/docs/helm/helm_template/)
