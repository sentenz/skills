---
name: github-actions
description: >-
  Designs, reviews, secures, and troubleshoots GitHub Actions workflows, reusable workflows, and composite actions. Use when creating or modifying files under `.github/workflows` or `.github/actions`, diagnosing workflow failures, hardening permissions and secrets, implementing CI/CD, or discussing GitHub Actions events, runners, matrices, caching, artifacts, environments, OIDC, or workflow reuse.
license: Apache-2.0
metadata:
  version: "1.0.0"
---

# GitHub Actions

Instructions for AI agents designing, reviewing, securing, and troubleshooting GitHub Actions automation.

- [1. Response Contract](#1-response-contract)
- [2. Workflow](#2-workflow)
- [3. Diagnose Before Generating](#3-diagnose-before-generating)
- [4. When to Use This Skill](#4-when-to-use-this-skill)
- [5. Non-Negotiable Guardrails](#5-non-negotiable-guardrails)
- [6. Architecture Principles](#6-architecture-principles)
- [7. Authoring Standards](#7-authoring-standards)
- [8. Security Model](#8-security-model)
- [9. Reliability and Efficiency](#9-reliability-and-efficiency)
- [10. Validation](#10-validation)
- [11. Review Checklist](#11-review-checklist)
- [12. References](#12-references)

## 1. Response Contract

Every GitHub Actions response must include:

1. **Execution context**
   > Identify the triggering event, trusted and untrusted inputs, runner type, operating systems, repository visibility, branch protections, required checks, and deployment environments. State assumptions when context is unavailable.

2. **Permissions and credential model**
   > State the required `GITHUB_TOKEN` permissions, whether secrets are available, whether OIDC is used, and which jobs cross a trust boundary. Default to no permissions and grant only the minimum required per job.

3. **Chosen design and trade-offs**
   > Explain the job graph, reuse boundary, caching or artifact strategy, concurrency behavior, and any portability or maintainability trade-offs.

4. **Validation plan**
   > Provide exact static checks and relevant GitHub-side verification steps. Include negative-path testing for event filters, fork pull requests, cancellation, retries, and deployment protections when applicable.

5. **Operational notes**
   > Describe rollout, observability, failure recovery, and rollback for workflows that publish, deploy, mutate repository state, or manage infrastructure.

Never treat workflow YAML as ordinary configuration. It is executable code with access to repository content, tokens, secrets, artifacts, caches, runners, and external systems.

## 2. Workflow

1. **Inspect repository policy**
   > Read `AGENTS.md`, `CONTRIBUTING.md`, existing workflows, organization conventions, branch protection assumptions, and dependency update configuration before generating changes.

2. **Classify the automation**
   > Determine whether the task is CI validation, release automation, deployment, repository maintenance, security scanning, a reusable workflow, a composite action, or workflow troubleshooting.

3. **Map trust boundaries**
   > Identify which event data or checked-out code may be controlled by an untrusted contributor. Treat pull request metadata, issue bodies, comments, branch names, commit messages, artifacts, and cache contents as untrusted unless provenance is established.

4. **Design permissions first**
   > Define `permissions: {}` at workflow scope where practical, then grant the smallest permission set to the specific job that requires it. Keep `id-token: write`, package publishing, pull-request writes, and deployment credentials isolated.

5. **Choose the reuse boundary**
   > Use reusable workflows for multi-job orchestration, composite actions for repeated step sequences, workflow templates for discoverable starter workflows, and ordinary jobs for local logic that does not justify an abstraction.

6. **Implement deterministically**
   > Pin external actions and cross-repository reusable workflows to full-length commit SHAs, specify runner labels deliberately, set timeouts, make shell behavior explicit, and avoid implicit credential persistence.

7. **Validate in layers**
   > Parse YAML, lint Actions semantics, lint embedded shell, scan for workflow security weaknesses, inspect the rendered job graph, and execute representative GitHub-hosted runs.

8. **Review operational behavior**
   > Verify cancellation, concurrency, retry safety, artifact retention, cache invalidation, deployment approvals, and rollback before finalizing.

9. **Emit the Response Contract**
   > Summarize context, permissions, design, validation, and operations in the final response.

## 3. Diagnose Before Generating

| Category | Common symptoms or request | Primary reference |
|---|---|---|
| Workflow syntax and event routing | Invalid YAML, unexpected triggers, skipped jobs, path or branch filters, expression errors | [Workflow Authoring](references/workflow-authoring.md) |
| Job architecture | Job dependencies, matrices, services, containers, concurrency, timeouts, outputs | [Workflow Authoring](references/workflow-authoring.md) |
| Security hardening | Excessive permissions, unsafe events, script injection, unpinned actions, secret leakage, runner compromise | [Security Hardening](references/security-hardening.md) |
| Cloud authentication and deployment | Long-lived cloud secrets, OIDC, environments, approvals, deployment serialization | [Security Hardening](references/security-hardening.md) |
| Reuse and governance | Reusable workflows, composite actions, templates, organization-wide CI, versioning | [Reuse and Architecture](references/reuse-and-architecture.md) |
| Validation and failures | Static linting, failed runs, flaky jobs, logs, reruns, local emulation, debugging | [Testing and Troubleshooting](references/testing-and-troubleshooting.md) |

Load only the references needed for the task. Load multiple references when a change crosses architecture, security, and operational boundaries.

## 4. When to Use This Skill

**Activate when:**

- Creating, reviewing, or modifying workflow files in `.github/workflows/`.
- Creating or reviewing composite actions under `.github/actions/`.
- Designing CI, release, deployment, maintenance, or security automation.
- Implementing reusable workflows, matrices, caching, artifacts, environments, or OIDC.
- Troubleshooting workflow syntax, event behavior, runner failures, permissions, secrets, or expressions.
- Reviewing workflow supply-chain and untrusted-input risks.

**Do not use for:**

- GitHub API integration that does not run through GitHub Actions.
- General shell scripting without workflow context.
- CI systems other than GitHub Actions, except for migration planning.
- Creating standalone JavaScript or Docker actions when the request is primarily action implementation rather than workflow integration; use the relevant language or container skill alongside this skill.

## 5. Non-Negotiable Guardrails

- Never execute or check out untrusted pull request code in a privileged `pull_request_target` or privileged `workflow_run` context.
- Never interpolate untrusted context values directly into `run:` scripts. Pass them through environment variables or structured action inputs and quote them correctly.
- Never grant write permissions at workflow scope when only one job requires them.
- Never add `id-token: write` outside the job that performs OIDC authentication.
- Never store long-lived cloud credentials when the target supports GitHub OIDC.
- Never print secrets, tokens, credentials, signed URLs, or sensitive command output. Treat redaction as defense in depth, not a guarantee.
- Never use untrusted artifacts or caches in a privileged job without validation and provenance controls.
- Never use self-hosted runners for untrusted public pull requests. Treat persistent or broadly networked runners as high-impact assets.
- Never reference an external action or cross-repository reusable workflow by a mutable branch or tag in security-sensitive workflows. Use a verified full-length commit SHA and retain a version comment for maintainability.
- Never deploy or publish from an unreviewed build when provenance, approvals, or branch protections are required.

## 6. Architecture Principles

### 6.1. Separate Validation from Privilege

Use unprivileged workflows for builds and tests. Place repository writes, publishing, or deployment in separate jobs or workflows that consume reviewed and verified outputs.

```plaintext
untrusted change
    |
    v
read-only validation --> reviewed commit or approved environment
                              |
                              v
                     privileged publish/deploy
```

Privilege separation must include event selection, token permissions, secret availability, artifact provenance, and runner isolation. A separate job alone is insufficient when it consumes attacker-controlled state.

### 6.2. Prefer Explicit Job Graphs

- Model dependencies with `needs` rather than relying on file order.
- Keep build, test, package, publish, and deploy responsibilities distinct.
- Use job outputs for small control data and artifacts for files.
- Keep the critical path short; parallelize independent jobs.
- Use a final aggregation job when branch protection requires one stable check across conditional or matrix jobs.

### 6.3. Reuse at Stable Boundaries

| Need | Preferred mechanism |
|---|---|
| Repeated steps within or across repositories | Composite action |
| Repeated multi-job pipeline | Reusable workflow |
| Discoverable starter configuration | Workflow template |
| Repository-specific orchestration | Ordinary workflow |
| Shared script with independent tests | Versioned script or package invoked by workflows |

Avoid abstractions that hide permissions, event assumptions, environment use, or deployment behavior from callers.

### 6.4. Treat Workflows as Production Software

- Keep interfaces typed and documented.
- Version shared automation.
- Review dependency updates.
- Test failure and cancellation paths.
- Preserve logs and evidence appropriate to the risk level.
- Require code ownership for workflow and shared automation changes where governance permits.

## 7. Authoring Standards

### 7.1. File and Identifier Naming

- Use lowercase kebab-case file names such as `pull-request-ci.yml` and `release-package.yml`.
- Use concise workflow names that describe the outcome, not the implementation.
- Use stable, machine-readable job IDs and human-readable job names.
- Name steps that perform meaningful work; omit names only for self-evident setup steps.
- Use explicit `run-name` when manual, release, or deployment runs need operator context.

### 7.2. Trigger Design

- Specify activity types and branch, tag, or path filters deliberately.
- Prefer `pull_request` for validating pull requests.
- Use `push` for trusted branch and tag automation.
- Use `workflow_dispatch` for explicit operator-driven actions with typed inputs.
- Use `schedule` only when timing drift is acceptable and idempotency is designed.
- Use `workflow_run` only with a documented trust model for the upstream workflow and its artifacts.
- Avoid `pull_request_target` unless repository-base context is essential and no untrusted code is executed.

### 7.3. Permissions

Start with no workflow-level permissions when compatible with the design:

```yaml
permissions: {}
```

Grant permissions per job:

```yaml
jobs:
  test:
    permissions:
      contents: read

  publish:
    permissions:
      contents: read
      packages: write
```

Do not grant `contents: write`, `pull-requests: write`, `issues: write`, `packages: write`, `security-events: write`, or `id-token: write` without a specific operation that requires it.

### 7.4. External Dependencies

Use full-length commit SHAs for external actions and cross-repository reusable workflows. Preserve the release identifier in a comment so dependency automation and reviewers can understand the intended version.

```yaml
- uses: actions/checkout@<full-length-commit-sha> # v4
  with:
    persist-credentials: false
```

Audit the source, publisher, required permissions, inputs, outputs, runtime, and release history before adoption. Configure Dependabot or an equivalent updater for GitHub Actions dependencies.

### 7.5. Shell and Expression Safety

- Make the shell explicit when behavior matters.
- Use strict error handling and quote expansions.
- Pass context values through `env` rather than embedding expressions in shell source.
- Use `$GITHUB_OUTPUT`, `$GITHUB_ENV`, and `$GITHUB_PATH` instead of deprecated workflow commands.
- Use multiline delimiters only when the content is trusted or the delimiter is generated safely.
- Keep complex logic in tested scripts rather than large inline `run:` blocks.

### 7.6. Time and Resource Bounds

- Set `timeout-minutes` for every job that can hang or consume costly runners.
- Set step timeouts for network, deployment, and teardown operations when supported by the design.
- Use `strategy.max-parallel` to control external-system load.
- Use concurrency groups for supersedable validation and serialized deployment.
- Set artifact retention intentionally and avoid uploading unnecessary files.

## 8. Security Model

### 8.1. Trust Classification

| Source | Default trust |
|---|---|
| Code from the default branch after required review | Trusted according to repository policy |
| Pull request head from a fork | Untrusted |
| Pull request metadata, issue content, comments, branch names, commit messages | Untrusted |
| External action or reusable workflow | Third-party executable dependency |
| Artifact from another workflow | Untrusted until producer and content are verified |
| Cache restored across trust boundaries | Potentially attacker-influenced |
| Self-hosted runner state and network | Sensitive persistent execution environment |
| Repository, environment, or organization secret | Sensitive credential material |

### 8.2. Credential Hierarchy

Prefer, in order:

1. Job-scoped `GITHUB_TOKEN` with minimum permissions.
2. OIDC-issued short-lived credentials with restrictive subject and audience conditions.
3. GitHub App installation tokens with narrow repository and permission scope.
4. Fine-grained personal access tokens only when platform limitations require them.
5. Classic personal access tokens or long-lived cloud keys only as an explicitly documented exception.

### 8.3. Deployment Controls

- Use protected environments for production and other sensitive targets.
- Require reviewers and branch or tag restrictions where available.
- Put credentials in the environment rather than broad repository scope when access should be gated.
- Use concurrency to prevent overlapping deployments to the same target.
- Separate build and deploy; deploy the exact reviewed artifact rather than rebuilding after approval.
- Record artifact digest, source commit, workflow identity, environment, and deployment result.

See [Security Hardening](references/security-hardening.md) for threat-specific controls and examples.

## 9. Reliability and Efficiency

- Use matrices for supported platform or version combinations, not for unrelated tasks.
- Use `fail-fast: false` when all matrix results are diagnostically valuable; keep the default when early cancellation saves substantial cost.
- Cache dependency downloads, not build outputs that require provenance or long-term retention.
- Key caches with lock files and relevant toolchain or platform dimensions.
- Use artifacts to pass immutable files between jobs and retain evidence.
- Design release, publish, and deploy jobs to be idempotent or safely resumable.
- Use concurrency with `cancel-in-progress: true` for superseded branch validation; do not cancel irreversible operations without an explicit recovery design.
- Prefer GitHub-hosted ephemeral runners unless hardware, network, compliance, or performance requirements justify self-hosting.
- Pin runner operating systems when reproducibility is more important than automatic image updates; otherwise monitor image changes.

## 10. Validation

Use the validation ladder appropriate to the change:

1. **Structure**
   > Parse YAML 1.2, verify files are under `.github/workflows/`, check frontmatter or metadata for composite actions, and validate referenced local paths.

2. **Actions semantics**
   > Run `actionlint` or an equivalent semantic linter against every changed workflow.

3. **Embedded code**
   > Run ShellCheck, PSScriptAnalyzer, language linters, and unit tests for referenced scripts or actions.

4. **Security**
   > Review permissions, action pinning, event trust, untrusted expressions, secrets, OIDC conditions, caches, artifacts, and runners. Use CodeQL workflow analysis, OpenSSF Scorecard, or an equivalent workflow security scanner where available.

5. **GitHub execution**
   > Run representative events on GitHub-hosted runners. Test successful, failing, cancelled, rerun, fork, and protected-environment paths as applicable.

6. **Operational evidence**
   > Verify logs, summaries, artifacts, attestations, retention, deployment records, and rollback instructions.

See [Testing and Troubleshooting](references/testing-and-troubleshooting.md) for commands and failure playbooks.

## 11. Review Checklist

Before finalizing a GitHub Actions change, verify:

- [ ] Events and filters match the intended execution set.
- [ ] Fork and untrusted-input behavior is explicitly safe.
- [ ] Workflow-level permissions are empty or read-only.
- [ ] Each job has only the permissions it needs.
- [ ] Secrets are scoped and are not exposed to untrusted code.
- [ ] OIDC replaces long-lived cloud credentials where supported.
- [ ] External actions and workflows are pinned to verified full commit SHAs.
- [ ] Checkout credential persistence is disabled unless a later Git operation requires it.
- [ ] Jobs and network operations have timeouts.
- [ ] Concurrency behavior is intentional.
- [ ] Caches and artifacts do not cross trust boundaries unsafely.
- [ ] Reusable workflow inputs, secrets, outputs, and permissions form a documented contract.
- [ ] Self-hosted runner exposure is justified and isolated.
- [ ] Static linting and embedded-script checks pass.
- [ ] Required checks, deployment approvals, retries, cancellation, and rollback have been considered.

## 12. References

- [Workflow Authoring](references/workflow-authoring.md)
- [Security Hardening](references/security-hardening.md)
- [Reuse and Architecture](references/reuse-and-architecture.md)
- [Testing and Troubleshooting](references/testing-and-troubleshooting.md)
- GitHub Docs: [Workflow syntax for GitHub Actions](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
- GitHub Docs: [Secure use reference](https://docs.github.com/en/actions/reference/security/secure-use)
- GitHub Docs: [OpenID Connect](https://docs.github.com/en/actions/concepts/security/openid-connect)
- GitHub Docs: [Reuse workflows](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows)
