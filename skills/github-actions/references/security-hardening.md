# Security Hardening

> **Part of:** [GitHub Actions](../SKILL.md)
> **Purpose:** Threat modeling, permissions, untrusted input, supply-chain security, credentials, runners, artifacts, and deployments

- [1. Threat Model](#1-threat-model)
- [2. Token Permissions](#2-token-permissions)
- [3. Untrusted Input and Script Injection](#3-untrusted-input-and-script-injection)
- [4. Pull Request Event Safety](#4-pull-request-event-safety)
- [5. Actions and Workflow Dependencies](#5-actions-and-workflow-dependencies)
- [6. Secrets, OIDC, and Environments](#6-secrets-oidc-and-environments)
- [7. Runners](#7-runners)
- [8. Caches and Artifacts](#8-caches-and-artifacts)
- [9. Release and Deployment Integrity](#9-release-and-deployment-integrity)
- [10. Security Review Procedure](#10-security-review-procedure)
- [11. Common Mistakes](#11-common-mistakes)
- [12. References](#12-references)

## 1. Threat Model

A GitHub Actions threat model must identify:

- Who can trigger the workflow.
- Who controls the checked-out commit.
- Which event fields are attacker-controlled.
- Which token permissions are available.
- Which repository, organization, and environment secrets are available.
- Which external actions, workflows, containers, and packages execute.
- Whether caches, artifacts, or outputs cross workflow boundaries.
- Whether the runner is ephemeral or persistent.
- Which networks, cloud accounts, registries, signing systems, and deployment targets are reachable.
- Which repository settings, branches, tags, releases, issues, pull requests, packages, or security alerts the workflow can modify.

### 1.1. Trust Boundary Table

| Boundary | Threat | Required control |
|---|---|---|
| Fork pull request to repository workflow | Arbitrary code and metadata | Read-only token, no secrets, ephemeral runner |
| Unprivileged build to privileged deploy | Artifact substitution or tampering | Provenance verification, digest binding, approval |
| Workflow to third-party action | Supply-chain compromise | Source review, full-SHA pin, minimum permissions |
| Workflow to cloud provider | Credential theft or over-broad role | OIDC, restrictive claims, short session, least privilege |
| Workflow to self-hosted runner | Persistence and lateral movement | Isolation, ephemeral lifecycle, restricted network, runner groups |
| Cache or artifact producer to consumer | Poisoning, path traversal, unexpected content | Scope, validate, verify producer and digest |

## 2. Token Permissions

### 2.1. Default Deny

Prefer:

```yaml
permissions: {}
```

Then add permissions to individual jobs. A job that checks out code normally requires only:

```yaml
permissions:
  contents: read
```

### 2.2. Permission Review

| Permission | Typical legitimate operation | Review concern |
|---|---|---|
| `contents: write` | Create tags, releases, or commits | Repository takeover if untrusted code executes |
| `pull-requests: write` | Comment, label, or update pull requests | Spam, metadata manipulation, approval confusion |
| `issues: write` | Create or update issues | Untrusted content propagation and spam |
| `packages: write` | Publish packages | Supply-chain compromise |
| `security-events: write` | Upload code-scanning results | Usually limited to security analysis jobs |
| `id-token: write` | Request an OIDC token | Enables cloud or service authentication according to trust policy |
| `attestations: write` | Create artifact attestations | Bind only to reviewed artifacts and trusted workflows |
| `actions: write` | Manage workflow runs | Broad automation control; rarely needed |

`id-token: write` does not itself grant cloud access, but it allows the job to request an identity token. The external trust policy determines what that identity can obtain.

### 2.3. Token Selection

Use the narrowest viable credential:

1. `GITHUB_TOKEN` with job-level permissions.
2. OIDC-issued external credentials.
3. GitHub App installation token.
4. Fine-grained personal access token.
5. Classic personal access token only as a documented exception.

Do not use a personal token merely to bypass permission design or event restrictions.

## 3. Untrusted Input and Script Injection

GitHub expressions are evaluated before an inline shell script is generated. Direct interpolation can turn data into executable syntax.

### 3.1. Unsafe

```yaml
- name: Check title
  run: echo "${{ github.event.pull_request.title }}"
```

A malicious title can escape the intended quoting and inject shell commands.

### 3.2. Safer Inline Script

```yaml
- name: Check title
  env:
    PR_TITLE: ${{ github.event.pull_request.title }}
  run: printf '%s\n' "$PR_TITLE"
```

The expression becomes an environment value rather than shell source. Shell quoting and downstream validation remain necessary.

### 3.3. Preferred Structured Input

Use a maintained action or tested script that accepts the value as a structured input or argument.

```yaml
- name: Validate title
  uses: example/validate-title@<full-length-commit-sha> # v2
  with:
    title: ${{ github.event.pull_request.title }}
```

The action itself must still treat the input as untrusted.

### 3.4. Untrusted Context Examples

Treat these as untrusted when contributor-controlled:

- Pull request title, body, labels, and head branch.
- Issue title, body, labels, and comments.
- Commit messages and author fields.
- Release or discussion content.
- File names, archive entries, package metadata, and test names.
- Manual input provided by an operator.
- Matrix values generated from repository content or API responses.

Never use untrusted values directly in commands, file paths, SQL, regular expressions, URLs, concurrency groups that carry authority, or cloud role selectors without validation.

## 4. Pull Request Event Safety

### 4.1. `pull_request`

Use for building and testing proposed code.

Expected properties:

- The code may be attacker-controlled.
- Fork pull requests normally receive a read-only token.
- Repository secrets are not exposed to fork pull requests.
- The runner must be treated as compromised after executing the code.

Keep these jobs read-only and ephemeral.

### 4.2. `pull_request_target`

This event runs in the context of the base repository and can receive elevated permissions and secrets. Use it only for operations on trusted base-repository code, such as labeling or commenting based on validated metadata.

Never:

- Check out the pull request head.
- Execute scripts from the pull request.
- Install dependencies from the pull request.
- Build a container or package from the pull request.
- Restore an attacker-controlled cache and then run privileged code.
- Download an unverified artifact produced from the pull request and execute it.

Safe pattern:

```yaml
name: Pull Request Metadata

on:
  pull_request_target:
    types:
      - opened
      - edited
      - synchronize

permissions: {}

jobs:
  label:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    permissions:
      pull-requests: write
    steps:
      - name: Apply validated metadata rule
        uses: example/metadata-policy@<full-length-commit-sha> # v1
        with:
          title: ${{ github.event.pull_request.title }}
```

This pattern does not check out or execute pull request code.

### 4.3. `workflow_run`

A privileged follow-up workflow may be useful for publishing results from an unprivileged build, but it must verify:

- The upstream workflow identity.
- The event and branch that produced the run.
- The exact source commit.
- The upstream conclusion.
- The artifact name, digest, expected files, and content constraints.
- That artifacts or caches cannot overwrite trusted executable paths.

Use a protected environment for the privileged operation and prefer attestations or signed provenance for high-value releases.

## 5. Actions and Workflow Dependencies

### 5.1. Pinning

Pin every external action and cross-repository reusable workflow to a verified full-length commit SHA.

```yaml
- uses: actions/checkout@<full-length-commit-sha> # v4
```

A tag or branch can move. Keep the human-readable release in a comment and use dependency automation to propose reviewed SHA updates.

For local actions and same-repository reusable workflows, the caller and callee come from the same commit when using a relative path.

### 5.2. Dependency Review

Before adopting an action or workflow, inspect:

- Ownership and publisher identity.
- Source code and generated distribution files.
- Requested token permissions.
- Secret and environment access.
- Network destinations.
- Runtime and transitive package dependencies.
- Release process, maintenance activity, and security policy.
- Input handling and shell execution.
- Whether the action modifies git configuration, credentials, workspace files, or runner state.

### 5.3. Checkout

Disable persisted credentials unless later steps require authenticated Git operations:

```yaml
- uses: actions/checkout@<full-length-commit-sha> # v4
  with:
    persist-credentials: false
```

Set `fetch-depth` only as deep as required. Fetching full history increases time and exposure without benefit when the job only needs the current commit.

### 5.4. Dependency Updates

Configure Dependabot for the `github-actions` ecosystem or an equivalent reviewed update process. Review changed SHAs, release notes, source diffs, permissions, and runtime changes before merging.

## 6. Secrets, OIDC, and Environments

### 6.1. Secret Rules

- Store one logical secret per value rather than structured blobs when practical.
- Scope secrets to the narrowest repository, environment, or organization audience.
- Do not pass secrets to jobs that execute untrusted code.
- Do not expose secrets through command arguments, process lists, debug output, artifacts, caches, summaries, or generated files.
- Register derived sensitive values for masking when they may appear in logs.
- Rotate a secret immediately after suspected exposure; deleting a log is not sufficient.
- Treat secret redaction as pattern matching that can fail after transformation.

### 6.2. OIDC

Prefer OIDC for cloud providers and services that support it.

```yaml
jobs:
  deploy:
    environment: production
    permissions:
      contents: read
      id-token: write
    steps:
      - name: Authenticate to cloud provider
        uses: provider/login-action@<full-length-commit-sha> # v3
        with:
          role: production-deployer
```

The cloud trust policy should restrict claims such as:

- Repository identity.
- Repository owner or organization.
- Branch, tag, or protected environment.
- Reusable workflow identity.
- Audience.
- Repository visibility or custom properties where supported.

Grant a short session with a narrowly scoped role. Do not trust only the organization when a specific repository or workflow is required.

### 6.3. Environments

Use environments to gate sensitive jobs:

```yaml
jobs:
  deploy:
    environment:
      name: production
      url: ${{ steps.deploy.outputs.url }}
```

Configure protection rules outside the workflow:

- Required reviewers.
- Allowed branches or tags.
- Wait timers where appropriate.
- Environment-scoped secrets and variables.
- Custom protection rules when available.

Remember that reusable workflow callers cannot pass environment secrets through `workflow_call`; environment selection in the called job determines the environment secret source.

## 7. Runners

### 7.1. GitHub-Hosted Runners

Prefer GitHub-hosted runners for untrusted or general workloads because they are ephemeral for each job. Still assume the job can access all data provided to that runner during execution.

- Do not expose unnecessary secrets.
- Review runner-image updates.
- Pin toolchains where reproducibility matters.
- Avoid relying on undocumented preinstalled software.

### 7.2. Self-Hosted Runners

Do not use self-hosted runners for untrusted public pull requests.

For private workloads, require:

- Ephemeral or just-in-time runner lifecycle where possible.
- Clean machine or virtual-machine state for every job.
- Dedicated runner groups and repository allow lists.
- Minimal host credentials and no developer keys.
- Restricted network routes and metadata-service access.
- No shared writable workspace between trust domains.
- Centralized patching, logging, inventory, and incident response.
- Capacity controls that prevent concurrent jobs from observing each other.

A container alone is not a sufficient isolation boundary for hostile workflow code.

## 8. Caches and Artifacts

### 8.1. Cache Threats

Caches are mutable optimization data. A less-trusted workflow may poison content later restored by a privileged workflow.

Controls:

- Separate keys by trust level, branch, operating system, architecture, and lock-file state.
- Avoid broad restore keys in privileged workflows.
- Never execute cached binaries or scripts in a privileged context without verification.
- Never cache credentials or deployment state.
- Prefer reinstalling security-sensitive dependencies from a verified lock file.

### 8.2. Artifact Threats

Artifacts can contain executable files, archives, symlinks, path traversal entries, unexpected file types, or replaced outputs.

Controls:

- Verify the producing workflow, run, branch, commit, and conclusion.
- Download only the expected artifact by exact name.
- Enforce size and file-count limits.
- Extract into an isolated directory with path traversal and symlink checks.
- Verify checksums, signatures, or attestations.
- Do not place untrusted artifact contents over scripts, tool directories, or the workspace used by privileged steps.

## 9. Release and Deployment Integrity

For release and deployment workflows:

1. Build once from a reviewed source commit.
2. Produce immutable artifacts with digests.
3. Run tests and scans against those exact artifacts.
4. Create attestations or provenance where supported.
5. Require protected-environment approval for sensitive targets.
6. Authenticate with OIDC or another short-lived credential.
7. Deploy or publish the exact verified artifact.
8. Record commit, digest, workflow run, environment, and result.
9. Define rollback to a known artifact rather than rebuilding old source.

Do not publish from a pull request workflow or from a mutable branch reference without a reviewed trust path.

## 10. Security Review Procedure

1. Enumerate all triggers and actors that can invoke them.
2. Identify the checked-out ref and code provenance in every job.
3. Mark every expression that can contain attacker-controlled data.
4. Record workflow- and job-level permissions.
5. Record secrets, environment access, and OIDC permissions.
6. List external actions, reusable workflows, containers, and package installation commands.
7. Verify full-SHA pins and publisher provenance.
8. Inspect caches, artifacts, job outputs, and cross-workflow data flows.
9. Review runner persistence and network reachability.
10. Test fork, cancellation, rerun, and failed-upstream behavior.
11. Confirm environment protections and rollback.
12. Run static and security analysis.

## 11. Common Mistakes

- Setting `permissions: write-all` to fix an authorization error.
- Granting `id-token: write` globally.
- Assuming a secret is safe because logs usually redact it.
- Using `pull_request_target` to build a contributor's code.
- Interpolating pull request or issue text directly into Bash or PowerShell.
- Pinning only third-party actions while leaving first-party actions mutable.
- Trusting an artifact because it came from another workflow in the same repository.
- Restoring a pull-request cache in a privileged release job.
- Using a shared persistent runner across repositories with different trust levels.
- Storing cloud access keys when OIDC is available.
- Rebuilding after approval instead of promoting the reviewed artifact.
- Allowing workflow changes without designated review or code ownership.

## 12. References

- GitHub Docs: [Secure use reference](https://docs.github.com/en/actions/reference/security/secure-use)
- GitHub Docs: [OpenID Connect](https://docs.github.com/en/actions/concepts/security/openid-connect)
- GitHub Docs: [Use GITHUB_TOKEN for authentication in workflows](https://docs.github.com/en/actions/tutorials/authenticate-with-github_token)
- GitHub Docs: [Securely using pull_request_target](https://docs.github.com/en/actions/reference/security/secure-use#using-the-pull_request_target-event)
- GitHub Docs: [Deployments and environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)
- GitHub Docs: [Self-hosted runners reference](https://docs.github.com/en/actions/reference/runners/self-hosted-runners)
- GitHub Docs: [Using artifact attestations to establish provenance for builds](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/establish-provenance)
