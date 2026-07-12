# Workflow Authoring

> **Part of:** [GitHub Actions](../SKILL.md)
> **Purpose:** Workflow syntax, event routing, job architecture, matrices, caching, artifacts, and concurrency

- [1. Design Sequence](#1-design-sequence)
- [2. Workflow Skeleton](#2-workflow-skeleton)
- [3. Events and Filters](#3-events-and-filters)
- [4. Jobs, Steps, and Conditions](#4-jobs-steps-and-conditions)
- [5. Matrices](#5-matrices)
- [6. Concurrency and Cancellation](#6-concurrency-and-cancellation)
- [7. Caches and Artifacts](#7-caches-and-artifacts)
- [8. Containers and Services](#8-containers-and-services)
- [9. Shells and Scripts](#9-shells-and-scripts)
- [10. CI Example](#10-ci-example)
- [11. Common Mistakes](#11-common-mistakes)
- [12. References](#12-references)

## 1. Design Sequence

Design workflows in this order:

1. Define the outcome and required check names.
2. Select events and filters.
3. Classify trusted and untrusted inputs.
4. Define workflow-level permissions.
5. Draw the job dependency graph.
6. Assign runner, environment, permissions, timeout, and concurrency to each job.
7. Define data transfer through outputs, artifacts, or caches.
8. Select external actions and pin them.
9. Implement scripts and conditions.
10. Validate success, failure, cancellation, and rerun behavior.

Do not begin with a copied workflow and retrofit the threat model afterward.

## 2. Workflow Skeleton

A production workflow should make intent, scope, permissions, and cancellation behavior visible near the top.

```yaml
name: Pull Request CI

run-name: >-
  CI for ${{ github.event.pull_request.number || github.ref_name }}

on:
  pull_request:
    branches:
      - main
  workflow_dispatch:

permissions: {}

concurrency:
  group: ci-${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true

defaults:
  run:
    shell: bash

jobs:
  test:
    name: Test
    runs-on: ubuntu-latest
    timeout-minutes: 20
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@<full-length-commit-sha> # v4
        with:
          persist-credentials: false
      - name: Run tests
        run: ./scripts/test.sh
```

### 2.1. Ordering Convention

Use a consistent top-level order:

1. `name`
2. `run-name`
3. `on`
4. `permissions`
5. `concurrency`
6. `env`
7. `defaults`
8. `jobs`

Within a job, prefer:

1. `name`
2. `if`
3. `needs`
4. `runs-on` or `uses`
5. `environment`
6. `concurrency`
7. `timeout-minutes`
8. `permissions`
9. `strategy`
10. `container` and `services`
11. `env` and `defaults`
12. `outputs`
13. `steps`, `with`, or `secrets`

Consistency is more important than the exact order, provided security-sensitive settings remain easy to review.

## 3. Events and Filters

### 3.1. Event Selection

| Event | Appropriate use | Important constraint |
|---|---|---|
| `pull_request` | Build and test proposed changes | Fork code is untrusted; secrets are unavailable by default |
| `push` | Trusted branch or tag automation | Validate branch and tag filters carefully |
| `workflow_dispatch` | Manual operation | Use typed inputs and protected environments for sensitive actions |
| `schedule` | Periodic maintenance | Runs may be delayed; make tasks idempotent |
| `workflow_call` | Reusable workflow entry point | Inputs and secrets form a public contract |
| `workflow_run` | Follow-up after another workflow | Treat upstream artifacts and branch identity as untrusted until verified |
| `pull_request_target` | Base-repository metadata automation | Never execute or check out untrusted PR code in the privileged context |
| `merge_group` | Merge queue validation | Include when required checks must run in a merge queue |

### 3.2. Filters

- Use `branches` and `tags` to narrow trusted release paths.
- Use `paths` only when skipped checks will not block required-status behavior.
- Remember that branch and path filters are combined with logical AND when both are present.
- Keep negative patterns after positive patterns when exclusion order matters.
- Include workflow files, build scripts, lock files, and shared configuration in path filters when they affect the result.

### 3.3. Required-Check Stability

A workflow skipped by branch or path filtering can leave an expected check pending. For monorepos or heavily conditional pipelines, use one of these patterns:

- Make the required workflow always start and decide work at the job level.
- Add a stable aggregation job that always reports the final result.
- Use separate required checks per component only when branch protection can model them accurately.
- Avoid renaming required workflow or job checks without coordinating branch protection changes.

### 3.4. Manual Inputs

Use typed inputs and validate semantic constraints in the first job.

```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        description: Deployment target
        required: true
        type: choice
        options:
          - staging
          - production
      dry_run:
        description: Plan without applying
        required: true
        default: true
        type: boolean
```

Do not use free-form manual input for a branch, environment, command, or file path without strict validation.

## 4. Jobs, Steps, and Conditions

### 4.1. Job Graph

Use `needs` to encode dependencies and make outputs explicit.

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      artifact-name: ${{ steps.meta.outputs.artifact-name }}
    steps:
      - id: meta
        run: echo "artifact-name=package-${GITHUB_SHA}" >> "$GITHUB_OUTPUT"

  verify:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - run: printf '%s\n' '${{ needs.build.outputs.artifact-name }}'
```

Keep job outputs small and non-sensitive. Use artifacts for files and external stores for large or durable data.

### 4.2. Conditions

- Prefer job-level `if` when an entire job is optional.
- Prefer step-level `if` for local branching within a job.
- Treat all values from `github.event` as untrusted strings unless documented otherwise.
- Use status functions deliberately: `success()`, `failure()`, `cancelled()`, and `always()`.
- For cleanup, prefer a condition that does not run after cancellation when continued execution would be unsafe.
- Avoid complex expressions duplicated across jobs; compute a validated decision once and expose it as an output.

### 4.3. Check Aggregation

A stable final check is useful when jobs are conditional or matrix-generated.

```yaml
jobs:
  lint:
    # ...

  test:
    # ...

  ci-result:
    name: CI Result
    if: ${{ !cancelled() }}
    needs:
      - lint
      - test
    runs-on: ubuntu-latest
    permissions: {}
    steps:
      - name: Verify required jobs
        env:
          LINT_RESULT: ${{ needs.lint.result }}
          TEST_RESULT: ${{ needs.test.result }}
        run: |
          test "$LINT_RESULT" = success
          test "$TEST_RESULT" = success
```

Account for intentionally skipped jobs when implementing an aggregator.

## 5. Matrices

Use matrices for the Cartesian product of a coherent test dimension such as operating system, language version, database version, or feature flag.

```yaml
strategy:
  fail-fast: false
  max-parallel: 6
  matrix:
    os:
      - ubuntu-latest
      - windows-latest
    runtime:
      - "20"
      - "22"
    include:
      - os: ubuntu-latest
        runtime: "22"
        coverage: true
```

### 5.1. Matrix Rules

- Quote version-like values to prevent YAML numeric coercion.
- Use `include` for exceptional combinations and added metadata.
- Use `exclude` only for known-invalid combinations; document why.
- Use `max-parallel` to protect rate-limited or stateful dependencies.
- Avoid placing deployment environments in a broad matrix unless protection and concurrency are defined per target.
- Do not use a matrix when a generated list would be attacker-controlled without validation.

## 6. Concurrency and Cancellation

### 6.1. Supersedable Validation

```yaml
concurrency:
  group: ci-${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true
```

This cancels stale validation for the same pull request or branch.

### 6.2. Serialized Deployment

```yaml
jobs:
  deploy:
    concurrency:
      group: deploy-production
      cancel-in-progress: false
```

Use a stable group per target. Do not cancel an in-progress irreversible deployment unless the deployment system supports safe interruption and recovery.

### 6.3. Concurrency Rules

- Include the workflow name in broad repository-level groups to avoid accidental cross-workflow cancellation.
- Normalize case-sensitive input before using it in a group when multiple spellings could refer to one target.
- Do not include secrets in concurrency expressions.
- Design teardown and state locks for cancelled runs.

## 7. Caches and Artifacts

### 7.1. Decision Table

| Requirement | Use |
|---|---|
| Speed up repeated dependency downloads | Cache |
| Pass files between jobs in one run | Artifact |
| Retain test reports or release evidence | Artifact |
| Publish a release deliverable | Release/package registry plus digest |
| Share mutable state | External state service, not cache |

### 7.2. Cache Rules

- Never cache secrets, credentials, signing keys, or mutable deployment state.
- Key on operating system, architecture, toolchain, dependency manager, and lock-file hash as needed.
- Use restore keys only when stale or broader content is safe.
- Treat caches from untrusted workflows as potentially poisoned.
- Do not use a cache as a provenance-bearing build artifact.

Example key:

```yaml
key: >-
  deps-${{ runner.os }}-${{ runner.arch }}-${{ hashFiles('**/package-lock.json') }}
```

### 7.3. Artifact Rules

- Give artifacts deterministic names.
- Set retention intentionally.
- Upload only required paths and fail when critical files are missing.
- Record checksums for release or deployment artifacts.
- Validate file type, size, paths, and provenance before consuming artifacts in a privileged job.
- Avoid extracting untrusted archives without zip-slip and symlink protections.

## 8. Containers and Services

- Pin container images by digest for security-sensitive jobs.
- Use service containers for disposable test dependencies.
- Add explicit health checks before tests begin.
- Avoid mounting the Docker socket into untrusted jobs.
- Treat container credentials as secrets and minimize registry scope.
- Remember that Linux container jobs and service containers require Linux runners.

Example service:

```yaml
services:
  postgres:
    image: postgres:17@sha256:<image-digest>
    env:
      POSTGRES_PASSWORD: test-only-password
    ports:
      - 5432:5432
    options: >-
      --health-cmd "pg_isready"
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
```

Use non-sensitive test credentials only in workflow source.

## 9. Shells and Scripts

### 9.1. Bash

Use explicit Bash and strict handling:

```yaml
defaults:
  run:
    shell: bash
```

For non-trivial logic, move commands into a versioned script:

```yaml
- name: Validate project
  env:
    TARGET: ${{ inputs.target }}
  run: ./scripts/validate.sh "$TARGET"
```

The script should use:

```bash
#!/usr/bin/env bash
set -euo pipefail
```

### 9.2. PowerShell

Use `pwsh`, set strict mode, and fail on errors:

```powershell
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
```

### 9.3. Workflow Files

Use environment files:

```bash
printf 'name=%s\n' "$value" >> "$GITHUB_OUTPUT"
printf 'KEY=%s\n' "$value" >> "$GITHUB_ENV"
printf '%s\n' "$directory" >> "$GITHUB_PATH"
```

Generate a collision-resistant delimiter when writing multiline values. Never allow untrusted input to choose the delimiter.

## 10. CI Example

The following template demonstrates read-only pull request validation, matrix testing, pinned dependencies, caching, timeouts, and stable aggregation. Replace placeholder SHAs with verified full-length commit SHAs.

```yaml
name: Pull Request CI

on:
  pull_request:
    branches:
      - main
  merge_group:

permissions: {}

concurrency:
  group: ci-${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true

defaults:
  run:
    shell: bash

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    timeout-minutes: 10
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@<full-length-commit-sha> # v4
        with:
          persist-credentials: false
      - name: Lint
        run: ./scripts/lint.sh

  test:
    name: Test (${{ matrix.os }}, runtime ${{ matrix.runtime }})
    runs-on: ${{ matrix.os }}
    timeout-minutes: 20
    permissions:
      contents: read
    strategy:
      fail-fast: false
      matrix:
        os:
          - ubuntu-latest
          - windows-latest
        runtime:
          - "20"
          - "22"
    steps:
      - uses: actions/checkout@<full-length-commit-sha> # v4
        with:
          persist-credentials: false
      - uses: actions/setup-node@<full-length-commit-sha> # v4
        with:
          node-version: ${{ matrix.runtime }}
          cache: npm
      - name: Install dependencies
        run: npm ci
      - name: Test
        run: npm test

  ci-result:
    name: CI Result
    if: ${{ !cancelled() }}
    needs:
      - lint
      - test
    runs-on: ubuntu-latest
    timeout-minutes: 5
    permissions: {}
    steps:
      - name: Verify results
        env:
          LINT_RESULT: ${{ needs.lint.result }}
          TEST_RESULT: ${{ needs.test.result }}
        run: |
          test "$LINT_RESULT" = success
          test "$TEST_RESULT" = success
```

## 11. Common Mistakes

- Assuming YAML file order controls job execution instead of using `needs`.
- Omitting `merge_group` when merge queue requires the same checks.
- Using path filters for a required check without a stable skipped-path design.
- Leaving workflow or job permissions implicit.
- Using mutable action tags without a security exception.
- Reusing cache keys across trusted and untrusted workflows.
- Passing files through job outputs instead of artifacts.
- Uploading the entire workspace, including credentials or temporary files, as an artifact.
- Using matrices for unrelated jobs or uncontrolled dynamic values.
- Omitting timeouts from network, test, publish, or deployment jobs.
- Embedding large scripts in YAML where they cannot be tested independently.
- Treating `ubuntu-latest` as a fixed operating-system image.

## 12. References

- GitHub Docs: [Workflow syntax for GitHub Actions](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
- GitHub Docs: [Events that trigger workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)
- GitHub Docs: [Running variations of jobs in a workflow](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/run-job-variations)
- GitHub Docs: [Control the concurrency of workflows and jobs](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency)
- GitHub Docs: [Dependency caching reference](https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching)
- GitHub Docs: [Store and share data with workflow artifacts](https://docs.github.com/en/actions/tutorials/store-and-share-data)
