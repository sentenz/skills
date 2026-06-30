---
name: terraform-skill
description: Use when writing, reviewing, or debugging Terraform/OpenTofu modules, tests, CI/CD, security scans, compliance policies, or state operations. Delegates to Anton Babenko's external Terraform skill for diagnose-first, version-aware guidance.
license: Apache-2.0
metadata:
  author: Anton Babenko
  version: "1.17.1"
  source: https://github.com/antonbabenko/terraform-skill
  external: true
---

# Terraform Skill

External Agent Skill registry entry for [antonbabenko/terraform-skill](https://github.com/antonbabenko/terraform-skill).

This entry registers the Terraform/OpenTofu skill in the catalog while preserving the upstream project as the source of truth.

## Upstream

- Repository: https://github.com/antonbabenko/terraform-skill
- Skill path: `skills/terraform-skill/SKILL.md`
- License: Apache-2.0
- Author: Anton Babenko

## Installation

```bash
npx skills add https://github.com/antonbabenko/terraform-skill
```

## Scope

Activate this skill for Terraform or OpenTofu work involving:

- Module design and review.
- Native Terraform tests, `terraform test`, Terratest, and mock providers.
- CI/CD workflows for plan/apply promotion.
- Security scanning, compliance policy, and secret-handling review.
- Remote state, locking, migration, and recovery operations.

## Source Control

Treat the upstream repository as authoritative for the full workflow and reference material. When updating this registry entry, check the upstream skill version and preserve attribution.
