# Reuse and Architecture

> **Part of:** [GitHub Actions](../SKILL.md)
> **Purpose:** Reusable workflows, composite actions, templates, contracts, versioning, and organization governance

- [1. Reuse Decision Matrix](#1-reuse-decision-matrix)
- [2. Reusable Workflows](#2-reusable-workflows)
- [3. Composite Actions](#3-composite-actions)
- [4. Workflow Templates](#4-workflow-templates)
- [5. Contracts and Compatibility](#5-contracts-and-compatibility)
- [6. Secrets and Permissions](#6-secrets-and-permissions)
- [7. Versioning and Distribution](#7-versioning-and-distribution)
- [8. Organization Architecture](#8-organization-architecture)
- [9. Migration Strategy](#9-migration-strategy)
- [10. Common Mistakes](#10-common-mistakes)
- [11. References](#11-references)

## 1. Reuse Decision Matrix

| Mechanism | Best for | Boundary | Limitations |
|---|---|---|---|
| Reusable workflow | Multi-job pipelines, shared permissions and orchestration | Called at job level | Caller cannot insert arbitrary steps into the called job |
| Composite action | Repeated step sequence | Called within a job step | Shares caller runner and job permissions; no independent jobs |
| Workflow template | Discoverable starter workflow | Copied into consuming repository | Copies diverge unless separately maintained |
| Local script or package | Complex tested logic | Called by steps or actions | Requires language/runtime lifecycle |
| Ordinary workflow | Repository-specific orchestration | Entire workflow | Duplication if organization-wide behavior repeats |

Use the smallest abstraction that makes the contract clearer. Do not reuse merely to reduce line count.

## 2. Reusable Workflows

Reusable workflows are stored directly in `.github/workflows/` and expose `workflow_call`.

```yaml
name: Reusable CI

on:
  workflow_call:
    inputs:
      runtime:
        description: Runtime version
        required: true
        type: string
      upload-coverage:
        description: Upload coverage report
        required: false
        default: false
        type: boolean
    secrets:
      coverage-token:
        description: Coverage service token
        required: false
    outputs:
      artifact-name:
        description: Name of the generated package artifact
        value: ${{ jobs.build.outputs.artifact-name }}

permissions: {}

jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    permissions:
      contents: read
    outputs:
      artifact-name: ${{ steps.meta.outputs.artifact-name }}
    steps:
      - uses: actions/checkout@<full-length-commit-sha> # v4
        with:
          persist-credentials: false
      - id: meta
        run: echo "artifact-name=package-${GITHUB_SHA}" >> "$GITHUB_OUTPUT"
```

Caller:

```yaml
jobs:
  ci:
    uses: example/automation/.github/workflows/ci.yml@<full-length-commit-sha> # v2
    permissions:
      contents: read
    with:
      runtime: "22"
      upload-coverage: true
    secrets:
      coverage-token: ${{ secrets.COVERAGE_TOKEN }}
```

### 2.1. Reusable Workflow Rules

- Call reusable workflows at the job level with `jobs.<job_id>.uses`.
- Type every input as `boolean`, `number`, or `string`.
- Document defaults, allowed values, security assumptions, and output semantics.
- Keep environment selection explicit and auditable.
- Use a matrix in the caller when one reusable workflow should run for multiple targets.
- Keep nesting shallow even though GitHub supports multiple levels.
- Remember that permissions can be maintained or reduced through a call chain, not elevated by a nested workflow.
- Pass secrets only to the direct workflow that needs them.

## 3. Composite Actions

A composite action packages repeated steps and executes within the caller's job, runner, workspace, network, token permissions, and secret exposure.

`action.yml`:

```yaml
name: Setup Project
description: Install the toolchain and project dependencies

inputs:
  runtime:
    description: Runtime version
    required: true

runs:
  using: composite
  steps:
    - uses: actions/setup-node@<full-length-commit-sha> # v4
      with:
        node-version: ${{ inputs.runtime }}
        cache: npm
    - shell: bash
      run: npm ci
```

Caller:

```yaml
- uses: ./.github/actions/setup-project
  with:
    runtime: "22"
```

### 3.1. Composite Action Rules

- Define descriptions for the action and every input and output.
- Specify `shell` for every `run` step.
- Use `$GITHUB_ACTION_PATH` to locate files bundled with the action.
- Do not assume repository root or caller working directory unless documented.
- Do not hide permissions or secret requirements; composite actions inherit the caller's job context.
- Keep orchestration, environment protection, matrices, and services in workflows rather than composite actions.
- Use tested scripts for complex logic inside the action.

## 4. Workflow Templates

Workflow templates help repositories create an initial workflow from an organization-controlled template. Use them when repositories need discoverable, customizable starting points rather than centrally enforced behavior.

Templates should:

- Include comments identifying required customization.
- Use safe permissions and pinned dependencies.
- Avoid organization-specific secrets that are not universally available.
- Link to maintenance and support documentation.
- Include a configuration file with applicable repository categories where required.

Do not use templates when a centrally updated reusable workflow is the actual requirement.

## 5. Contracts and Compatibility

Treat shared workflow and action interfaces as APIs.

### 5.1. Input Contract

For each input, define:

- Name and type.
- Required or optional status.
- Default.
- Allowed values and validation.
- Whether the value may be untrusted.
- Whether it influences permissions, environments, runners, commands, paths, or cloud roles.

Do not allow caller input to select arbitrary runners, environments, commands, action references, or privileged roles without an allow list.

### 5.2. Secret Contract

For each secret, define:

- Purpose.
- Minimum external permissions.
- Source scope: repository, environment, or organization.
- Jobs and steps that receive it.
- Whether OIDC can replace it.
- Rotation and failure behavior.

Prefer named secret passing to `secrets: inherit`. Use inheritance only when the caller and callee are tightly governed and the expanded secret surface is understood.

### 5.3. Output Contract

Outputs should be:

- Small.
- Non-sensitive.
- Deterministic.
- Documented for empty, skipped, and failed cases.

Use artifacts for files and retain their digest and provenance where appropriate.

### 5.4. Compatibility

Classify changes:

| Change | Compatibility |
|---|---|
| Add optional input with safe default | Usually backward compatible |
| Add output | Usually backward compatible |
| Change default behavior | Potentially breaking |
| Rename or remove input, secret, or output | Breaking |
| Increase required permissions | Security-relevant and potentially breaking |
| Change runner or environment assumptions | Potentially breaking |
| Change artifact name or format | Breaking for consumers |

Publish migration notes for breaking changes.

## 6. Secrets and Permissions

### 6.1. Permission Propagation

The caller should define permissions for the reusable-workflow job. The called workflow cannot elevate beyond what the caller grants.

```yaml
jobs:
  release:
    permissions:
      contents: write
      id-token: write
    uses: example/automation/.github/workflows/release.yml@<full-length-commit-sha> # v3
```

The called workflow should still document and declare its expected permissions so callers can review the contract.

### 6.2. Secret Propagation

Secrets are passed only to directly called workflows. In a chain A to B to C, B must explicitly pass a secret onward to C.

Use named passing:

```yaml
secrets:
  registry-token: ${{ secrets.REGISTRY_TOKEN }}
```

Avoid broad inheritance for reusable workflows that call other workflows or accept untrusted inputs.

### 6.3. Environment Secrets

Environment secrets are selected by the job's `environment` in the called workflow. They are not passed through `on.workflow_call`. Keep environment ownership and deployment behavior visible to callers.

## 7. Versioning and Distribution

### 7.1. References

For cross-repository use, callers should pin to a full commit SHA:

```yaml
uses: example/automation/.github/workflows/ci.yml@<full-length-commit-sha> # v2.4.1
```

Maintain semantic release tags for discoverability, but resolve consumption to a verified SHA. Use dependency automation to update the SHA and version comment together.

### 7.2. Release Process

A shared automation release should include:

1. Static and security validation.
2. Integration tests in representative consumer repositories.
3. Compatibility review.
4. Versioned release notes.
5. Immutable commit reference.
6. Migration guidance for breaking changes.
7. Deprecation window for widely used interfaces.

### 7.3. Local Reuse

Use relative paths for same-repository reusable workflows and composite actions when caller and implementation must evolve atomically:

```yaml
uses: ./.github/workflows/ci.yml
```

```yaml
uses: ./.github/actions/setup-project
```

The reusable workflow path must be a direct child of `.github/workflows/`; subdirectories are not supported.

## 8. Organization Architecture

A mature organization can structure automation in layers:

```plaintext
organization policy and runner governance
                |
                v
central reusable workflows and composite actions
                |
                v
repository caller workflows with minimal orchestration
                |
                v
project scripts, tests, and deployment tooling
```

### 8.1. Central Layer

Central automation should provide:

- Secure defaults and minimum permissions.
- Standard build, test, scan, package, and deploy workflows.
- OIDC patterns and protected-environment contracts.
- Approved action dependencies and update automation.
- Common summaries, artifacts, attestations, and observability.
- Versioning, support ownership, and deprecation policy.

### 8.2. Repository Layer

Repository callers should define:

- Events and repository-specific filters.
- Required workflow inputs.
- Explicit permissions and secrets.
- Repository-specific environments and deployment targets.
- Project scripts and test commands.

### 8.3. Governance

Use repository and organization settings to complement workflow files:

- Restrict allowed actions and reusable workflows.
- Require full-SHA pinning where supported.
- Set default `GITHUB_TOKEN` permissions to read-only.
- Protect workflow paths with CODEOWNERS.
- Restrict self-hosted runner groups.
- Configure environment protections.
- Enable dependency graph, Dependabot, code scanning, and audit logging.

## 9. Migration Strategy

To consolidate duplicated workflows:

1. Inventory workflows and group them by behavior.
2. Identify stable common stages and repository-specific variation.
3. Define typed inputs, named secrets, outputs, permissions, and runner assumptions.
4. Create a reusable workflow or composite action with integration tests.
5. Migrate one low-risk repository.
6. Compare checks, artifacts, duration, permissions, and failure behavior.
7. Publish a versioned release.
8. Migrate remaining repositories incrementally.
9. Remove copied logic only after consumers are verified.
10. Add dependency update and deprecation processes.

Avoid a large centralization change that simultaneously alters permissions, runners, toolchains, and deployment behavior.

## 10. Common Mistakes

- Creating a reusable workflow for a three-step sequence better represented by a composite action.
- Creating a composite action that hides deployment environments or broad permissions.
- Using untyped or undocumented inputs.
- Allowing input to choose arbitrary shell commands or runner labels.
- Using `secrets: inherit` by default.
- Assuming environment secrets can be passed through `workflow_call`.
- Pinning central workflows to a mutable `main` branch.
- Introducing breaking defaults without versioning.
- Nesting workflows until permissions and data flow become difficult to audit.
- Centralizing project-specific logic that should remain a tested repository script.
- Treating copied workflow templates as centrally updated dependencies.

## 11. References

- GitHub Docs: [Reuse workflows](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows)
- GitHub Docs: [Reusing workflow configurations](https://docs.github.com/en/actions/concepts/workflows-and-actions/reusing-workflow-configurations)
- GitHub Docs: [Creating a composite action](https://docs.github.com/en/actions/tutorials/creating-a-composite-action)
- GitHub Docs: [Creating workflow templates for an organization](https://docs.github.com/en/actions/how-tos/reuse-automations/create-workflow-templates)
- GitHub Docs: [Sharing actions and workflows from a private repository](https://docs.github.com/en/actions/how-tos/reuse-automations/share-across-private-repositories)
