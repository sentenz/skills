---
name: threat-modeling
description: |
  Performs structured threat modeling for software systems, web applications, APIs, cloud architectures, and microservices. Uses STRIDE for threat enumeration, PASTA for business-logic risk validation, LINDDUN for privacy analysis, Data Flow Diagrams (DFD) for architecture representation, CVSS v4.0 for severity scoring, MITRE ATT&CK Enterprise for technique mapping, and CWE for weakness classification. Produces a prioritized threat register with mitigations and risk scores.

  Use when performing threat modeling, creating a threat model, reviewing an architecture for security risks, identifying attack vectors, or building a threat register — even if the user says "check my design for issues" or "what could go wrong with this system." Also triggers for security design review, attack surface analysis, abuse case modeling, and secure design consultation.

  Do NOT use for OT/ICS systems with Microsoft TMT CSV exports (use threat-modeling-ics instead) or for writing security tests (use a testing skill instead).
metadata:
  version: "1.0.0"
  activation:
    implicit: true
    priority: 1
    triggers:
      - "threat model"
      - "threat modeling"
      - "stride"
      - "pasta"
      - "linddun"
      - "attack surface"
      - "data flow diagram"
      - "trust boundary"
      - "abuse case"
      - "security design review"
    match:
      languages: ["markdown", "yaml", "json"]
      paths:
        - "**/*threat-model*"
        - "**/*threat_model*"
        - "**/*security-design*"
        - "docs/security/**"
      prompt_regex: "(?i)(threat model|stride|pasta|linddun|attack surface|trust boundary|data flow diagram|abuse case|security design review|dfd)"
  usage:
    load_on_prompt: true
    autodispatch: true
---

# Threat Modeling

Instructions for AI security agents performing structured threat modeling for software systems, web applications, APIs, and cloud architectures.

> [!NOTE]
> Use this skill for general software and cloud threat modeling. For OT/ICS systems using Microsoft Threat Modeling Tool (TMT) CSV exports, use the [threat-modeling-ics](../threat-modeling-ics/SKILL.md) skill instead.

- [Expert Vocabulary Payload](#expert-vocabulary-payload)
- [Anti-Pattern Watchlist](#anti-pattern-watchlist)
- [1. Benefits](#1-benefits)
- [2. Principles](#2-principles)
- [3. Frameworks](#3-frameworks)
  - [3.1. STRIDE](#31-stride)
  - [3.2. PASTA](#32-pasta)
  - [3.3. LINDDUN](#33-linddun)
  - [3.4. CVSS](#34-cvss)
  - [3.5. MITRE ATT\&CK](#35-mitre-attck)
  - [3.6. CWE](#36-cwe)
- [4. Workflow](#4-workflow)
  - [4.1. Preparation](#41-preparation)
  - [4.2. Threat Enumeration](#42-threat-enumeration)
  - [4.3. Output](#43-output)
- [5. Deliverables](#5-deliverables)
- [6. Style Guide](#6-style-guide)
- [7. Template](#7-template)
  - [7.1. Threat Model Diagram](#71-threat-model-diagram)
  - [7.2. Threat Register Template](#72-threat-register-template)
- [8. References](#8-references)

## Expert Vocabulary Payload

**Threat Identification:**
STRIDE (Shostack), PASTA (UcedaVélez), LINDDUN (Deng et al.), attack surface enumeration, threat agent profiling, abuse case (McDermott), attacker capability model, attack tree (Schneier), misuse case

**Architecture Representation:**
Data Flow Diagram (DFD) (Yourdon-DeMarco), trust boundary, external entity, data store, data flow, process node, DFD decomposition, privilege boundary, Mermaid flowchart

**Scoring & Classification:**
CVSS v4.0 (FIRST), DREAD (Microsoft), MITRE ATT&CK Enterprise tactic and technique, CWE (MITRE), OWASP Top 10, risk prioritization matrix, exploitability assessment, impact analysis

**Mitigation:**
defense-in-depth, principle of least privilege, zero trust architecture (Kindervag), compensating control, countermeasure chaining, secure-by-design, OWASP ASVS control, NIST 800-53 control mapping

## Anti-Pattern Watchlist

Scan every threat model output against this list before delivery.

### 1. Enumeration Without Architecture
**Detection:** Threats are generated from a checklist or framework alone with no DFD or architecture diagram. Trust boundaries are not defined before threat enumeration begins.
**Resolution:** Create a DFD with labeled trust boundaries before enumerating threats. Architecture is the required input; threats are the derived output. Threats generated without architecture evidence cannot be verified or prioritized.

### 2. Single-Framework Lock-In
**Detection:** Only STRIDE threats are produced. Privacy threats (LINDDUN), business-logic risks (PASTA), or supply-chain risks are not considered for the system type.
**Resolution:** Apply STRIDE as the primary framework. Validate with PASTA for systems with business-critical workflows. Add LINDDUN analysis for systems that collect, process, or share personal data.

### 3. Generic Threat Actor
**Detection:** All threats reference a single generic "attacker" without capability, motivation, or access-level differentiation.
**Resolution:** Define at least two threat actors (e.g., external unauthenticated attacker, authenticated insider, compromised dependency) with capability and access before enumeration. CVSS scores must reflect the threat actor's actual access level.

### 4. Copy-Paste Mitigations
**Detection:** Multiple threats share identical mitigations such as "use encryption" or "add authentication" without specifics tied to the component or interface.
**Resolution:** Each mitigation must name the specific component, interface, data flow, and control. Link mitigations to a CWE weakness and an OWASP ASVS or NIST 800-53 control reference where applicable.

### 5. CVSS Inflation
**Detection:** All threats receive High or Critical CVSS v4.0 scores. No row has a Low or Medium score. Scores are assigned from the STRIDE category alone, not from the modeled attack path.
**Resolution:** Derive every CVSS vector from the specific attack vector (`AV`), attack complexity (`AC`), privileges required (`PR`), user interaction (`UI`), and impact metrics supported by the DFD and threat description. A defensible score requires a defensible vector.

### 6. Unjustified Not Applicable
**Detection:** Threats are dismissed as not applicable without naming the specific architectural constraint that eliminates the threat.
**Resolution:** Every "Not Applicable" decision must cite the architectural fact that makes the threat inapplicable (e.g., "component has no network exposure," "field is read-only, no user input accepted").

## 1. Benefits

- Shift-Left Security
  > Identifies vulnerabilities during design, when the cost to remediate is lowest and before code is written or deployed.

- Risk-Driven Prioritization
  > Combines severity (CVSS) and exploitability evidence to produce a prioritized threat register that directs security investment to the highest-impact findings.

- Traceability
  > Links architecture elements, threats, attacker techniques, underlying weaknesses, and mitigations in a single reviewable artifact for compliance, audits, and security backlogs.

- Framework Coverage
  > Combining STRIDE, PASTA, and LINDDUN ensures threats are identified across security, business logic, and privacy dimensions.

## 2. Principles

- Architecture First
  > Build the Data Flow Diagram before enumerating threats. Threats must be grounded in architecture evidence: components, trust boundaries, and data flows.

- Threat Actor Modeling
  > Define threat actors with capability, motivation, and access level before threat enumeration. CVSS metrics must reflect actual threat actor access, not worst-case assumptions.

- Evidence-Based Decisions
  > Do not assign MITRE ATT&CK techniques, CWE IDs, CVSS scores, or mitigations without supporting evidence from the DFD, system documentation, or analyst justification.

- Additive Reviews
  > Threat modeling is iterative. New findings append to the register rather than replacing prior analysis. Preserve previous threat IDs and justifications.

## 3. Frameworks

### 3.1. STRIDE

Use STRIDE as the primary taxonomy for threat enumeration across all trust boundaries and data flows.

- Spoofing
  > Illegitimate use of an identity, credential, certificate, or endpoint to impersonate a legitimate actor or component.

- Tampering
  > Unauthorized modification of data at rest, data in transit, configuration, logic, or execution inputs.

- Repudiation
  > Inability to prove that an action, transaction, or event occurred or was performed by a specific actor.

- Information Disclosure
  > Unauthorized exposure of sensitive data, configuration, or secrets to an unintended party.

- Denial of Service
  > Interruption, degradation, exhaustion, or blocking of a service's availability to legitimate users.

- Elevation of Privilege
  > Acquisition of permissions or capabilities beyond the intended authorization boundary.

### 3.2. PASTA

Use PASTA (Process for Attack Simulation and Threat Analysis) to validate business-logic threats that STRIDE alone does not capture.

- Stage I — Define Objectives: identify business and security objectives, compliance requirements, and risk tolerance.
- Stage II — Define Technical Scope: enumerate components, APIs, data flows, and dependencies.
- Stage III — Decompose Application: build DFD, enumerate entry points, assets, and trust levels.
- Stage IV — Threat Analysis: enumerate threats using attacker-centric scenarios and attack trees.
- Stage V — Vulnerability Analysis: map threats to existing vulnerabilities in components and dependencies.
- Stage VI — Attack Modeling: model realistic attack paths using attack trees and MITRE ATT&CK techniques.
- Stage VII — Risk Analysis: prioritize threats by business impact and exploitability, define residual risk.

### 3.3. LINDDUN

Apply LINDDUN for systems that collect, process, transfer, or share personal data.

- Linkability
  > Ability to link two or more records, requests, or identities belonging to the same individual.

- Identifiability
  > Ability to identify a data subject within a dataset even when direct identifiers are removed.

- Non-repudiation
  > Inability of a data subject to deny an action, transaction, or record relating to them.

- Detectability
  > Ability to detect that a data item or communication about an individual exists even without accessing content.

- Disclosure of Information
  > Unauthorized exposure of personal data to parties without a lawful basis.

- Unawareness
  > Lack of data subject awareness about collection, processing, retention, or sharing of their personal data.

- Non-compliance
  > Processing of personal data outside the bounds of applicable law, regulation, or consent scope.

### 3.4. CVSS

Use [FIRST CVSS v4.0](https://www.first.org/cvss/) to score each threat when a meaningful exploitability and impact assessment is possible.

- CVSS Score
  > Record the CVSS v4.0 base score as a numeric value between `0.0` and `10.0`.

- CVSS Severity
  > Record the severity category: `None`, `Low`, `Medium`, `High`, or `Critical`.

- CVSS Vector
  > Record the full vector string: `CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:N/SI:N/SA:N`.

- Rationale Rule
  > The analyst justification must make the selected vector understandable from the DFD interaction and threat description.

### 3.5. MITRE ATT&CK

Use [MITRE ATT&CK Enterprise](https://attack.mitre.org/matrices/enterprise/) to map threats to realistic adversary behavior.

- Tactic and Technique IDs
  > Record the most relevant ATT&CK Enterprise tactic (e.g., `TA0001 Initial Access`) and technique ID (e.g., `T1190 Exploit Public-Facing Application`) when the threat description supports a reliable mapping.

- Blank When Ambiguous
  > Leave MITRE fields blank when the threat is too generic or design-level to support a reliable technique mapping. A blank is correct; a forced mapping is not.

### 3.6. CWE

Use [MITRE CWE](https://cwe.mitre.org/) to classify the underlying weakness that enables each threat.

- Specificity Rule
  > Prefer the most specific CWE supported by the threat description and justification.

- Multi-CWE Rule
  > Use comma-separated values when a finding depends on more than one concrete weakness.

## 4. Workflow

> [!IMPORTANT]
> Execute every step below in order. Do not skip, reorder, or merge steps. Stop at any blocking gate and wait for user input before continuing.

### 4.1. Preparation

1. Create or locate the threat model diagram

    **Action:** Locate or create a Data Flow Diagram (DFD) for the target system.
    - Search the current context for a Mermaid diagram or architecture document.
    - If found, extract components, trust boundaries, data flows, and external entities.
    - **Blocking gate:** If no diagram is available, ask the user for one of the following before continuing:
      - A Mermaid DFD or architecture diagram file.
      - External documentation or links describing the system architecture.
      - A description of system components and trust boundaries sufficient to draft a DFD.
    - Draft the Mermaid DFD from the provided input if one does not already exist, and save it as `<system-name>-threat-model.md`.
    - Do not proceed to step 2 until the diagram is available or the user explicitly waives this step.

2. Define threat actors

    **Action:** Define threat actors relevant to the system before enumeration.
    - Define at least two threat actors with capability and access level (e.g., external unauthenticated attacker, authenticated insider, compromised third-party component).
    - Record threat actors in the threat model document.

3. Identify applicable frameworks

    **Action:** Determine which frameworks apply based on system type.
    - Apply STRIDE to all systems.
    - Apply PASTA when the system has critical business workflows (e.g., payment processing, authorization decisions, data pipelines).
    - Apply LINDDUN when the system processes personal data.

### 4.2. Threat Enumeration

4. Enumerate threats per data flow and trust boundary

    **Action:** For each data flow crossing a trust boundary in the DFD, apply STRIDE categories.
    - Apply all six STRIDE categories to each trust boundary crossing.
    - Record only threats that are architecturally plausible given the modeled component types and data flows.
    - Leave MITRE ATT&CK, CWE, and CVSS fields blank when evidence is insufficient; prefer blank over forced values.

5. Assess each threat

    **Action:** For each threat row, populate the following fields in order.
    - `State`: `Not Started` → `Needs Investigation` → `Mitigated` / `Accepted` / `Not Applicable`.
    - `Priority`: `Low` / `Medium` / `High`.
    - `Justification`: a concise, technically grounded analyst statement.
    - `MITRE Tactic/Technique`: map to ATT&CK Enterprise when supportable.
    - `CWE ID`: classify the underlying weakness.
    - `CVSS v4.0 Vector / Score / Severity`: score when exploitability and impact can be assessed.
    - `Mitigation`: specify component-level countermeasures referencing OWASP ASVS or NIST 800-53 controls.

6. Validate decisions

    **Action:** Review decisions for consistency before producing the final output.
    - Check that all `Not Applicable` rows cite a specific architectural fact.
    - Check that CVSS vectors are derived from DFD evidence, not from STRIDE category alone.
    - Check that identical mitigations across multiple rows are still component-specific.

### 4.3. Output

7. Produce the threat register

    **Action:** Write the complete threat register to the output file.
    - Save as `<system-name>-threat-model-review.md` (Markdown table) or `<system-name>-threat-model-review.csv`.
    - Include the DFD and threat register in the same document or as linked files.
    - Verify that all required columns are present in the output.

## 5. Deliverables

When asked to perform or assist with threat modeling, produce the following.

1. DFD Document

    A `<system-name>-threat-model.md` containing the Mermaid DFD with labeled trust boundaries, components, and data flows.

2. Threat Register

    A `<system-name>-threat-model-review.md` or `.csv` with one row per threat, including STRIDE category, state, priority, justification, MITRE ID, CWE ID, CVSS vector/score/severity, and mitigation.

3. Review Summary

    A short Markdown summary including:
    - Threat counts by STRIDE category and state.
    - Highest-risk threats table (ID, Threat, Component, CVSS Score, Priority).
    - Top attack paths with MITRE ATT&CK technique mappings.
    - Key mitigations by priority (Immediate, Short-Term, Long-Term).
    - Evidence gaps and threats in `Needs Investigation`.

## 6. Style Guide

- Threat IDs
  > Assign sequential IDs (`TM-001`, `TM-002`, …) so threats are stable references in backlogs, audit reports, and issue trackers.

- Be specific with mappings
  > Only add MITRE ATT&CK technique IDs and CWE IDs that can be defended from the threat description and DFD evidence.

- Respect incomplete evidence
  > Blank MITRE, CWE, and CVSS fields are acceptable when a reliable mapping cannot be supported. Do not fill fields with templated values.

- Keep justifications concise
  > A good justification is technically grounded, names the specific component and interface, and is brief enough to remain readable in a table cell.

- Prefer architecture-backed judgment
  > Final state, CWE, CVSS, and mitigation decisions must be tied to the actual modeled component, trust boundary, and exploit path — not inherited from the STRIDE category alone.

## 7. Template

### 7.1. Threat Model Diagram

- `<system-name>-threat-model.md`
  > A Mermaid DFD showing components, trust boundaries, and data flows.

  ```mermaid
  flowchart TD
      %% External Entities
      subgraph External [External Entities]
          User((End User))
          Admin((Administrator))
          ExtAPI((External API))
      end

      %% Application Boundary
      subgraph AppBoundary [Trust Boundary: Application]
          WebApp[Web Application]
          API[REST API Service]
          AuthSvc[Authentication Service]
      end

      %% Data Boundary
      subgraph DataBoundary [Trust Boundary: Data Store]
          DB[(Primary Database)]
          Cache[(Cache Store)]
          SecretStore[(Secret Store)]
      end

      %% Data Flows
      User --> |"HTTPS (TLS 1.3)"| WebApp
      Admin --> |"HTTPS (TLS 1.3)"| WebApp
      WebApp --> |"Internal HTTP"| API
      API --> |"Internal gRPC"| AuthSvc
      API <--> |"SQL/TLS"| DB
      API <--> |"Redis Protocol"| Cache
      AuthSvc --> |"Internal HTTPS"| SecretStore
      API --> |"HTTPS (TLS 1.3)"| ExtAPI
  ```

### 7.2. Threat Register Template

- `<system-name>-threat-model-review.md`
  > Threat register with one row per identified threat.

  | ID     | Component     | Interaction            | Category    | Title                              | State             | Priority | Justification | MITRE Tactic/Technique | CWE ID  | CVSS v4.0 Vector                                               | CVSS Score | CVSS Severity | Mitigation                                               |
  | ------ | ------------- | ---------------------- | ----------- | ---------------------------------- | ----------------- | -------- | ------------- | ---------------------- | ------- | -------------------------------------------------------------- | ---------- | ------------- | -------------------------------------------------------- |
  | TM-001 | REST API      | User → WebApp → API   | Spoofing    | Unauthenticated API endpoint access | Needs Investigation | High  | API endpoint accepts requests without validating bearer token. Auth header is optional in current configuration. | TA0001 / T1190 | CWE-287 | CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N | 9.3 | Critical | Enforce authentication on all API endpoints. Implement OAuth 2.0 bearer token validation. Map to OWASP ASVS V2.1. |
  | TM-002 | Primary Database | API → DB           | Tampering   | SQL injection via unsanitized input | Mitigated        | High     | API uses parameterized queries (PDO). Input validation applied at API boundary. No dynamic SQL concatenation detected. | TA0040 / T1565.001 | CWE-89 | CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N | 8.7 | High | Parameterized queries enforced. Input validation with allowlist. Map to OWASP ASVS V5.3. |

## 8. References

- STRIDE [Threat Modeling](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats) guide.
- PASTA [Methodology](https://owasp.org/www-pdf-archive/AppSecEU2012_PASTA.pdf) overview.
- LINDDUN [Privacy Threat Modeling](https://linddun.org/) framework.
- OWASP [Threat Dragon](https://owasp.org/www-project-threat-dragon/) tool.
- FIRST [CVSS v4.0 Specification](https://www.first.org/cvss/v4.0/specification-document) page.
- FIRST [CVSS v4.0 Calculator](https://www.first.org/cvss/calculator/4.0) page.
- MITRE [ATT&CK Enterprise](https://attack.mitre.org/matrices/enterprise/) matrix.
- MITRE [CWE](https://cwe.mitre.org/) page.
- OWASP [ASVS](https://owasp.org/www-project-application-security-verification-standard/) standard.
- NIST [SP 800-154](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-154.pdf) guide to data-centric system threat modeling.
