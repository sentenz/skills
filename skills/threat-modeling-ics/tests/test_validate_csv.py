from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate_csv.py"
SKILL_ROOT = SCRIPT_PATH.parent.parent
SPEC = importlib.util.spec_from_file_location("validate_csv", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import validator from {SCRIPT_PATH}")
validate_csv = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validate_csv
SPEC.loader.exec_module(validate_csv)


PRIORITY_INPUTS = {
    "Info": ("Info", "None"),
    "Low": ("Info", "Medium"),
    "Medium": ("Info", "Critical"),
    "High": ("Low", "Critical"),
    "Critical": ("High", "Critical"),
}


def make_record(**overrides: str):
    row = {column: "" for column in validate_csv.EXPECTED_COLUMNS}
    row.update(
        {
            "Id": "test-1",
            "State": "Mitigated",
            "CVSS v4.0 Severity": "Medium",
            "Likelihood of Exploit": "Medium",
            "Risk Prioritization": "Medium",
            "Risk Treatment": "Mitigation",
            "Risk Approval": "Lead Security",
        }
    )
    row.update(overrides)
    if "Justification" not in overrides:
        treatment = row["Risk Treatment"]
        approval = row["Risk Approval"]
        if treatment == "Avoidance":
            row["Justification"] = (
                "The architecture decision records that the attack path is eliminated."
            )
        elif treatment == "Mitigation":
            row["Justification"] = (
                "Implemented controls: input validation within the device boundary. "
                "Residual risk is Low after validation, with malformed input exposure "
                "remaining. Treatment is Mitigation through those controls. "
                f"{approval} "
                "owns the residual risk and records approval in the risk register."
            )
        elif treatment == "Acceptance":
            row["Justification"] = (
                "Compensating controls: monitored access outside the device boundary. "
                "Residual risk is Low after monitoring, with limited exposure "
                "remaining. Treatment is Acceptance because the business accepts the "
                "remaining risk below the documented Low threshold. "
                f"{approval} owns the residual risk "
                "and records approval through the risk register."
            )
        elif treatment == "Transfer":
            row["Justification"] = (
                "Compensating controls: provider monitoring outside the device "
                "boundary. Residual risk is Low after monitoring, with service "
                "exposure remaining. Treatment is Transfer to Example Vendor under the "
                "named SLA for outage consequences."
            )
    return validate_csv.Record(
        tuple(
            validate_csv.Cell(
                row[column],
                column in validate_csv.QUOTED_COLUMNS,
            )
            for column in validate_csv.EXPECTED_COLUMNS
        )
    )


def validate(record):
    return validate_csv.validate_risk_governance(
        record,
        row_number=2,
        threat_id="test-1",
    )


class RiskGovernanceValidationTests(unittest.TestCase):
    def test_accepts_every_risk_matrix_combination(self):
        for likelihood, severity_map in validate_csv.RISK_MATRIX.items():
            for severity, expected_priority in severity_map.items():
                with self.subTest(likelihood=likelihood, severity=severity):
                    treatment = (
                        "Acceptance"
                        if expected_priority in {"Info", "Low"}
                        else "Mitigation"
                    )
                    approval = validate_csv.RISK_APPROVAL_MATRIX[
                        expected_priority
                    ][treatment]
                    findings = validate(
                        make_record(
                            **{
                                "CVSS v4.0 Severity": severity,
                                "Likelihood of Exploit": likelihood,
                                "Risk Prioritization": expected_priority,
                                "Risk Treatment": treatment,
                                "Risk Approval": approval,
                            }
                        )
                    )
                    self.assertEqual([], findings)

    def test_reports_priority_that_differs_from_matrix(self):
        findings = validate(
            make_record(
                **{
                    "CVSS v4.0 Severity": "Critical",
                    "Likelihood of Exploit": "High",
                    "Risk Prioritization": "Low",
                    "Risk Approval": "Executive",
                }
            )
        )

        self.assertEqual(1, len(findings))
        self.assertEqual("Risk Prioritization", findings[0].column)
        self.assertEqual("Critical", findings[0].expected)

    def test_unfinished_rows_require_blank_governance_fields(self):
        for state in validate_csv.UNFINISHED_STATES:
            with self.subTest(state=state):
                findings = validate(
                    make_record(
                        **{
                            "State": state,
                            "Risk Prioritization": "Low",
                            "Risk Treatment": "Acceptance",
                            "Risk Approval": "Product Security",
                        }
                    )
                )
                self.assertEqual(
                    {
                        "Risk Prioritization",
                        "Risk Treatment",
                        "Risk Approval",
                    },
                    {finding.column for finding in findings},
                )

    def test_enforces_state_and_priority_treatment_compatibility(self):
        cases = (
            (
                {
                    "State": "Not Applicable",
                    "Risk Treatment": "Mitigation",
                    "Risk Approval": "Product Security",
                },
                "Not Applicable requires Avoidance treatment",
            ),
            (
                {
                    "CVSS v4.0 Severity": "Medium",
                    "Likelihood of Exploit": "Info",
                    "Risk Prioritization": "Low",
                    "Risk Treatment": "Avoidance",
                    "Risk Approval": "Not Required",
                },
                "Mitigated uses an incompatible treatment",
            ),
            (
                {
                    "CVSS v4.0 Severity": "None",
                    "Likelihood of Exploit": "Info",
                    "Risk Prioritization": "Info",
                    "Risk Treatment": "Mitigation",
                    "Risk Approval": "Product Security",
                },
                "Risk Treatment is incompatible with Risk Prioritization",
            ),
        )

        for overrides, expected_message in cases:
            with self.subTest(expected_message=expected_message):
                treatment_findings = [
                    finding
                    for finding in validate(make_record(**overrides))
                    if finding.column == "Risk Treatment"
                ]
                self.assertEqual(1, len(treatment_findings))
                self.assertEqual(expected_message, treatment_findings[0].message)

    def test_enforces_approval_matrix_and_allows_escalation(self):
        for priority, (likelihood, severity) in PRIORITY_INPUTS.items():
            for treatment in validate_csv.RISK_TREATMENTS:
                state = "Not Applicable" if treatment == "Avoidance" else "Mitigated"
                minimum = validate_csv.RISK_APPROVAL_MATRIX[priority][treatment]
                base = {
                    "State": state,
                    "CVSS v4.0 Severity": severity,
                    "Likelihood of Exploit": likelihood,
                    "Risk Prioritization": priority,
                    "Risk Treatment": treatment,
                }
                with self.subTest(priority=priority, treatment=treatment):
                    minimum_findings = [
                        finding
                        for finding in validate(
                            make_record(**base, **{"Risk Approval": minimum})
                        )
                        if finding.column == "Risk Approval"
                    ]
                    self.assertEqual([], minimum_findings)

                    escalated_findings = [
                        finding
                        for finding in validate(
                            make_record(**base, **{"Risk Approval": "Executive"})
                        )
                        if finding.column == "Risk Approval"
                    ]
                    self.assertEqual([], escalated_findings)

                    minimum_index = validate_csv.RISK_APPROVAL_ROLES.index(minimum)
                    if minimum_index:
                        lower_role = validate_csv.RISK_APPROVAL_ROLES[
                            minimum_index - 1
                        ]
                        lower_findings = [
                            finding
                            for finding in validate(
                                make_record(
                                    **base,
                                    **{"Risk Approval": lower_role},
                                )
                            )
                            if finding.column == "Risk Approval"
                        ]
                        self.assertEqual(1, len(lower_findings))
                        self.assertEqual(
                            "Risk Approval is below the minimum required role",
                            lower_findings[0].message,
                        )

    def test_finalized_rows_reject_missing_risk_fields(self):
        findings = validate(
            make_record(
                **{
                    "CVSS v4.0 Severity": "",
                    "Likelihood of Exploit": "",
                    "Risk Prioritization": "",
                    "Risk Treatment": "",
                    "Risk Approval": "",
                }
            )
        )

        self.assertEqual(
            {
                "CVSS v4.0 Severity",
                "Likelihood of Exploit",
                "Risk Prioritization",
                "Risk Treatment",
                "Risk Approval",
            },
            {finding.column for finding in findings},
        )

    def test_rejects_noncanonical_risk_values(self):
        findings = validate(
            make_record(
                **{
                    "Risk Prioritization": "medium",
                    "Risk Treatment": "mitigate",
                    "Risk Approval": "lead security",
                }
            )
        )

        self.assertEqual(
            {"Risk Prioritization", "Risk Treatment", "Risk Approval"},
            {finding.column for finding in findings},
        )

    def test_enforces_treatment_evidence_requirements(self):
        cases = (
            (
                {
                    "State": "Not Applicable",
                    "Risk Treatment": "Avoidance",
                    "Risk Approval": "Not Required",
                    "Justification": "",
                },
                {"Avoidance lacks an architectural elimination decision"},
            ),
            (
                {"Justification": ""},
                {
                    "Mitigated treatment lacks enforcement-boundary control evidence",
                    "Mitigated treatment lacks a standardized residual-risk level",
                    "Risk Treatment lacks a documented decision rationale",
                    "Mitigation lacks a residual-risk owner",
                    "Mitigation lacks an approval mechanism",
                },
            ),
            (
                {
                    "Risk Treatment": "Acceptance",
                    "Risk Approval": "Lead Security",
                    "Justification": "",
                },
                {
                    "Mitigated treatment lacks enforcement-boundary control evidence",
                    "Mitigated treatment lacks a standardized residual-risk level",
                    "alternative Acceptance lacks a business rationale",
                    "Acceptance lacks an acceptance threshold",
                    "Acceptance lacks an approving stakeholder",
                    "Acceptance lacks an explicit approval mechanism",
                },
            ),
            (
                {
                    "Risk Treatment": "Transfer",
                    "Risk Approval": "Lead Security",
                    "Justification": "",
                },
                {
                    "Mitigated treatment lacks enforcement-boundary control evidence",
                    "Mitigated treatment lacks a standardized residual-risk level",
                    "alternative Risk Treatment lacks a documented decision rationale",
                    "Transfer lacks a named third party",
                    "Transfer lacks a specific transfer instrument",
                    "Transfer lacks an explicit risk scope",
                },
            ),
        )

        for overrides, expected_messages in cases:
            with self.subTest(treatment=overrides.get("Risk Treatment")):
                messages = {
                    finding.message for finding in validate(make_record(**overrides))
                }
                self.assertEqual(expected_messages, messages)

    def test_bundled_example_exposes_invalid_info_mitigation(self):
        findings = []
        output_records = validate_csv.read_records(
            SKILL_ROOT / "references" / "Example_Threat_Model_Generated.csv",
            origin="output",
            findings=findings,
        )
        source_records = validate_csv.read_source_records(
            SKILL_ROOT / "references" / "Example_Threat_Model.csv",
            findings,
        )
        findings.extend(validate_csv.validate_header(output_records))
        findings.extend(
            validate_csv.validate_rows(
                output_records,
                technique_index=validate_csv.load_attack_techniques(
                    validate_csv.DEFAULT_ATTACK_SOURCE
                ),
                weakness_index=validate_csv.load_cwe_weaknesses(
                    validate_csv.DEFAULT_CWE_SOURCE
                ),
                mitigation_index=validate_csv.load_emb3d_mitigations(
                    validate_csv.DEFAULT_EMB3D_MITIGATIONS
                ),
            )
        )
        findings.extend(validate_csv.validate_source(output_records, source_records))

        self.assertEqual(
            [
                (
                    "3",
                    "Risk Treatment",
                    "Risk Treatment is incompatible with Risk Prioritization",
                )
            ],
            [
                (finding.threat_id, finding.column, finding.message)
                for finding in findings
            ],
        )


if __name__ == "__main__":
    unittest.main()
