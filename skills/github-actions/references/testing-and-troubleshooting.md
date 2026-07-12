# Testing and Troubleshooting

> **Part of:** [GitHub Actions](../SKILL.md)
> **Purpose:** Validation layers, static analysis, GitHub-side testing, debugging, and failure playbooks

- [1. Validation Ladder](#1-validation-ladder)
- [2. Static Validation](#2-static-validation)
- [3. Security Validation](#3-security-validation)
- [4. GitHub-Side Testing](#4-github-side-testing)
- [5. Debug Logging](#5-debug-logging)
- [6. Failure Diagnosis](#6-failure-diagnosis)
- [7. Flaky and Slow Workflows](#7-flaky-and-slow-workflows)
- [8. Safe Reruns and Recovery](#8-safe-reruns-and-recovery)
- [9. Review Checklist](#9-review-checklist)
- [10. Common Mistakes](#10-common-mistakes)
- [11. References](#11-references)

## 1. Validation Ladder

Validate from cheapest and most deterministic to most integrated:

1. Repository conventions and changed-file review.
2. YAML 1.2 syntax and local path validation.
3. GitHub Actions semantic linting.
4. Embedded shell and language linting.
5. Security analysis.
6. Unit tests for scripts, custom actions, and generated matrices.
7. Representative GitHub-hosted workflow runs.
8. Fork, permission, environment, cancellation, rerun, and rollback tests.
9. Production-like canary or non-production deployment.

A successful YAML parse does not prove that GitHub accepts the workflow or that the workflow is secure.

## 2. Static Validation

### 2.1. Changed Files

Inspect the complete diff, including:

- `.github/workflows/*.yml` and `.yaml`.
- `.github/actions/**/action.yml` and `.yaml`.
- Scripts called by workflows.
- Dependency lock files.
- Dockerfiles and container references.
- CODEOWNERS, Dependabot, and repository policy files.
- Deployment manifests and infrastructure code.

Workflow behavior often changes through scripts or configuration outside `.github/workflows/`.

### 2.2. Actionlint

Use `actionlint` to validate workflow syntax, expressions, contexts, job dependencies, runner labels, and embedded shell integration.

```bash
actionlint
```

With ShellCheck available:

```bash
actionlint -shellcheck shellcheck
```

Run against changed files when the repository is large:

```bash
actionlint .github/workflows/pull-request-ci.yml
```

Do not suppress a rule without documenting why the workflow remains correct.

### 2.3. YAML Validation

Use a YAML 1.2-aware parser. YAML 1.1 parsers may incorrectly treat the key `on` as a Boolean. Verify:

- No duplicate keys.
- Indentation and scalar style.
- Quoted version values in matrices.
- Correct expression delimiters.
- Valid local action and reusable workflow paths.

### 2.4. Embedded Code

Run the native linter for every language embedded or invoked by the workflow:

```bash
shellcheck scripts/*.sh
```

```powershell
Invoke-ScriptAnalyzer -Path scripts -Recurse
```

Test scripts independently with controlled environment variables and temporary directories.

### 2.5. Composite Actions

Validate `action.yml` or `action.yaml`:

- Required top-level `name`, `description`, and `runs` fields.
- Input and output descriptions.
- `runs.using: composite` for composite actions.
- Explicit shell on every `run` step.
- Correct use of `$GITHUB_ACTION_PATH`.
- No hidden assumptions about caller permissions, working directory, or operating system.

## 3. Security Validation

Review or scan for:

- Mutable external action or reusable workflow references.
- Excessive workflow or job permissions.
- Direct expression interpolation into `run:`.
- Unsafe `pull_request_target` or `workflow_run` code checkout.
- Secrets exposed to untrusted code.
- OIDC permission or trust-policy overreach.
- Cache poisoning and unsafe artifact extraction.
- Self-hosted runners reachable by untrusted events.
- Checkout credential persistence.
- Unbounded network downloads or execution of generated code.
- Release or deployment from an unreviewed source.

Use CodeQL workflow analysis, OpenSSF Scorecard, and a dedicated workflow security scanner when supported by the repository.

Static findings are signals. Review event context and data flow before suppressing or accepting a result.

## 4. GitHub-Side Testing

### 4.1. Inspect Workflow Definitions

With GitHub CLI:

```bash
gh workflow list
```

```bash
gh workflow view pull-request-ci.yml --yaml
```

The repository default branch may determine which workflow definitions are discoverable for manual dispatch.

### 4.2. Manual Dispatch

For workflows that support `workflow_dispatch`:

```bash
gh workflow run deploy.yml \
  --ref feature/test-workflow \
  -f environment=staging \
  -f dry_run=true
```

Use a non-production environment and non-privileged credentials for initial validation.

### 4.3. Observe Runs

```bash
gh run list --workflow pull-request-ci.yml
```

```bash
gh run watch <run-id> --exit-status
```

```bash
gh run view <run-id> --log-failed
```

Inspect the event, source branch, source commit, actor, permissions, runner labels, job graph, artifacts, environment approvals, and conclusion.

### 4.4. Test Matrix

For meaningful changes, test:

| Path | Why |
|---|---|
| Success | Baseline correctness |
| Expected test failure | Failure propagation and summaries |
| Cancelled run | Cleanup and concurrency behavior |
| Rerun failed jobs | Idempotency and external side effects |
| Fork pull request | Token, secret, and untrusted-code safety |
| Internal pull request | Repository-specific permissions |
| Default-branch push | Trusted branch behavior |
| Tag or release | Release filter correctness |
| Protected environment | Approval and secret gating |
| Merge queue | Required-check compatibility |

### 4.5. Local Emulation

Local workflow emulators can shorten feedback for simple shell and container jobs, but they are not authoritative for:

- GitHub token permissions.
- Fork security behavior.
- Hosted runner images.
- Environments and protection rules.
- OIDC claims.
- Reusable workflow edge cases.
- Service behavior and networking.
- GitHub API event payloads.

Always finish validation on GitHub for changes that depend on platform semantics.

## 5. Debug Logging

### 5.1. Structured Logs

Use workflow commands to group related output:

```bash
echo "::group::Dependency diagnostics"
printenv | sort
npm --version
echo "::endgroup::"
```

Do not print all environment variables in jobs that receive secrets. Select non-sensitive diagnostics explicitly.

### 5.2. Step Summaries

Write concise diagnostic and test summaries to `$GITHUB_STEP_SUMMARY`:

```bash
{
  echo '## Test Summary'
  echo
  echo '- Unit tests: passed'
  echo '- Integration tests: passed'
} >> "$GITHUB_STEP_SUMMARY"
```

Never include secrets, signed URLs, or sensitive infrastructure details in summaries.

### 5.3. Debug Flags

GitHub supports runner and step debug logging through repository or organization secrets or variables such as `ACTIONS_RUNNER_DEBUG` and `ACTIONS_STEP_DEBUG` according to current platform guidance.

Enable them temporarily, reproduce the issue, inspect logs for sensitive output, then disable them. Rotate any credential that may have been exposed.

### 5.4. Temporary Diagnostics

Temporary diagnostics should:

- Be narrowly scoped.
- Avoid secret-bearing commands.
- Be removed before merge unless they provide durable observability.
- Use artifact retention appropriate to the sensitivity of captured data.

## 6. Failure Diagnosis

### 6.1. Workflow Does Not Start

Check:

- File path is directly under `.github/workflows/`.
- YAML and `on` syntax are valid.
- Event activity type matches.
- Branch, tag, and path filters match.
- Workflow exists on the branch required by the event.
- Manual workflow is enabled and visible on the default branch.
- Repository or organization Actions policy permits referenced actions.
- Commit message did not request a workflow skip.
- Merge queue emits `merge_group` and the workflow handles it.

### 6.2. Job Is Skipped

Check:

- `if` expression and implicit `success()` behavior.
- Results of every job in `needs`.
- Boolean versus string comparison.
- Availability of contexts at job and step evaluation time.
- Matrix expansion and `include` or `exclude` rules.
- Environment protection or concurrency state.

Inspect job condition logs in the GitHub UI when available.

### 6.3. Permission Denied

Check:

- Workflow- and job-level `permissions`.
- Repository default token policy.
- Fork pull request token restrictions.
- Organization policy.
- Whether a reusable workflow caller granted the required permissions.
- Whether the API operation requires a GitHub App or user token rather than `GITHUB_TOKEN`.
- Environment approval and secret availability.

Do not fix permission errors by granting `write-all`.

### 6.4. Secret Is Empty

Check:

- Fork or Dependabot event restrictions.
- Secret scope and environment selection.
- Secret name and caller-to-reusable-workflow mapping.
- Whether `secrets: inherit` is permitted and appropriate.
- Whether an `if` condition attempted to reference a secret directly where unsupported.
- Whether the secret is intentionally unavailable until environment approval.

### 6.5. Expression or Output Failure

Check:

- Step has an `id` before referencing `steps.<id>.outputs`.
- Producer wrote to `$GITHUB_OUTPUT`.
- Job maps step output before caller reads `needs.<job>.outputs`.
- Output is not secret-redacted or empty on a skipped path.
- JSON is valid before using `fromJSON`.
- Values are quoted when YAML might coerce numbers or Booleans.

### 6.6. Cache Miss or Corruption

Check:

- Exact key and restore key order.
- Lock-file hash and workspace path.
- Operating-system and architecture dimensions.
- Cache scope across branches.
- Whether an untrusted run populated a broader key.
- Whether the cached content is safe to reuse.

Delete or rotate a suspect cache key rather than repeatedly restoring corrupted state.

### 6.7. Artifact Missing or Unsafe

Check:

- Producer job completed and upload step ran.
- Artifact name matches exactly.
- Retention period has not expired.
- Hidden files and path globs behave as intended.
- Consumer selected the correct run and commit.
- Archive extraction and digest validation are safe.

## 7. Flaky and Slow Workflows

### 7.1. Flakiness

Classify failures before adding retries:

- Product or test defect.
- External service instability.
- Race condition.
- Resource exhaustion.
- Runner image drift.
- Dependency download or registry issue.
- Clock, locale, time zone, or order dependence.
- Shared-state collision.

A blind retry can hide a deterministic defect or repeat an unsafe side effect.

### 7.2. Performance

Measure job and step duration, then optimize:

- Parallelize independent jobs.
- Reduce checkout depth.
- Cache dependency downloads with correct keys.
- Avoid repeated setup across jobs when a reusable artifact is safer.
- Split fast required checks from expensive optional or scheduled checks.
- Use matrix `max-parallel` according to runner and external-system capacity.
- Cancel superseded pull request runs.
- Avoid uploading large, low-value artifacts.

Do not sacrifice isolation, provenance, or test coverage solely for runtime reduction.

### 7.3. Timeouts

Set timeouts based on observed healthy duration plus reasonable variance. A timeout should fail with enough log context to diagnose the blocked operation.

## 8. Safe Reruns and Recovery

Before rerunning a failed publish, release, deployment, or mutation job, determine:

- Which side effects completed.
- Whether the operation is idempotent.
- Whether an external lock or partial deployment remains.
- Whether a package version, tag, release, or artifact already exists.
- Whether credentials or approvals remain valid.
- Whether the source commit and artifact digest are unchanged.

Prefer a workflow designed to detect and resume or safely reject duplicate work. Do not rerun an irreversible job until current state is reconciled.

Rollback should identify:

- Last known-good artifact digest.
- Target environment or registry state.
- Commands or workflow dispatch needed to restore it.
- Data or schema compatibility constraints.
- Required approvals.
- Evidence to preserve for incident review.

## 9. Review Checklist

- [ ] Workflow YAML passes a YAML 1.2 parser.
- [ ] `actionlint` passes without unexplained suppressions.
- [ ] Shell and language linters pass.
- [ ] Local actions, scripts, and reusable workflow paths exist.
- [ ] External dependencies are full-SHA pinned.
- [ ] Security analysis covers permissions, events, inputs, credentials, artifacts, caches, and runners.
- [ ] Successful and failed GitHub-hosted runs were inspected.
- [ ] Fork and protected-environment behavior was tested where relevant.
- [ ] Cancellation, concurrency, and rerun behavior is safe.
- [ ] Logs and summaries provide useful non-sensitive diagnostics.
- [ ] Release or deployment rollback is documented.

## 10. Common Mistakes

- Treating YAML parse success as complete validation.
- Using a YAML 1.1 parser that converts `on` to a Boolean.
- Running only the happy path.
- Debugging by printing all environment variables.
- Adding retries before identifying the failure class.
- Rerunning a partially completed publish or deploy without reconciling state.
- Assuming local emulation reproduces GitHub permissions and security semantics.
- Ignoring scripts, Dockerfiles, or lock files changed alongside workflow YAML.
- Suppressing actionlint or security findings without a threat-model explanation.
- Forgetting merge queue and fork pull request test cases.

## 11. References

- GitHub Docs: [Troubleshooting workflows](https://docs.github.com/en/actions/how-tos/troubleshoot-workflows)
- GitHub Docs: [Using workflow run logs](https://docs.github.com/en/actions/how-tos/monitor-workflows/use-workflow-run-logs)
- GitHub Docs: [Enabling debug logging](https://docs.github.com/en/actions/how-tos/monitor-workflows/enable-debug-logging)
- GitHub Docs: [Re-running workflows and jobs](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs)
- GitHub CLI Manual: [`gh workflow`](https://cli.github.com/manual/gh_workflow)
- GitHub CLI Manual: [`gh run`](https://cli.github.com/manual/gh_run)
- Actionlint: [Static checker for GitHub Actions workflow files](https://github.com/rhysd/actionlint)
