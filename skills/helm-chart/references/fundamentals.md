# Chart contracts

A chart describes desired resources. A release identifies one deployment of the chart in a namespace. Helm renders values and templates, talks to the API server and records numbered revisions. Kubernetes controllers reconcile the resulting objects. A successful client render establishes only the first step. The default release storage uses Kubernetes Secrets; protect access to stored values and manifests.

| File or directory | Contract |
| --- | --- |
| Chart.yaml | Chart v2 uses a name, chart SemVer and API version. Use type application or library. Quote appVersion, which identifies the application and need not be SemVer. Use kubeVersion for the declared cluster range. |
| values.yaml, values.schema.json | Supply public defaults and a schema for merged values. Required keys, enums, ranges, mutually exclusive modes and conditional requirements fail early. A schema default is descriptive; put runtime defaults in values.yaml. |
| templates/, charts/, crds/ | Render templates, include dependencies, and install static CRDs before rendering custom resources on initial install. Separate CRD lifecycle ownership from ordinary resources. |
| .helmignore, README.md | Exclude development and local artifacts. Document external controllers, images, ports, required privileges, accepted values, upgrade caveats, tests and examples. Inspect the package itself. |

Compose inputs from chart defaults, parent overrides under the dependency name or alias, ordered values files, then command-line overrides. Later files win for the same key. Maps merge and lists replace. Quote string identifiers and use --set-string for a numeric-looking identifier. Compare upgrade behavior with the production controller's reset/reuse settings. A saved defaults dump can silently freeze old chart defaults.

In Go templates, dot is the current scope. Capture the original context before with or range, or pass it explicitly. A named template receives the context supplied to include. Use include with nindent for YAML fragments, toYaml for structured values, and quote for strings. Leave typed integer and boolean fields typed. Avoid default on an explicit false or zero when that value has meaning. Use required for a missing nonempty string and fail for a relation between two values. Avoid evaluating untrusted text through tpl.

Treat values keys, resource names, selectors, persistence and port names as public interfaces. A helper-only change can still alter them. Compare old and new renders with identical release coordinates before classifying a version bump. Source contracts are indexed in [Primary sources](sources.md).

For a versioned chart API, use a major bump for a breaking supported values or upgrade contract, minor for backwards-compatible features and patch for backwards-compatible fixes. Track upstream application SemVer separately when the application follows it. Verify the image digest and appVersion together on an application update.
