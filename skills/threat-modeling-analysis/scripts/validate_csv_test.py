"""Regression tests for threat-model risk approval validation."""

import csv
import importlib.util
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("validate_csv.py").resolve()
SKILL = SCRIPT.parents[1]
SPEC = importlib.util.spec_from_file_location("validate_csv", SCRIPT)
VALIDATOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VALIDATOR
SPEC.loader.exec_module(VALIDATOR)


def row(**overrides):
    fields = dict.fromkeys(VALIDATOR.EXPECTED_COLUMNS, "")
    fields.update({
        "Id": "42",
        "State": "Mitigated",
        "Description": "A device interface exposes an attack path.",
        "Justification": "Verified controls limit the remaining exposure.",
        "ATT&CK ID": "N/A",
        "EMB3D TID": "N/A",
        "CWE ID": "N/A",
        "Risk Prioritization": "High",
        "Risk Treatment": "Mitigation",
        "Risk Approval": "CPSO",
    })
    fields.update(overrides)
    return fields


def artifact(*rows):
    stream = io.StringIO()
    writer = csv.DictWriter(
        stream,
        fieldnames=VALIDATOR.EXPECTED_COLUMNS,
        delimiter=";",
        quoting=csv.QUOTE_ALL,
    )
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def validate(*rows):
    return VALIDATOR.validate_rows(VALIDATOR.parse_records(artifact(*rows)))


class RiskApprovalTests(unittest.TestCase):
    def test_all_matrix_cells_require_exact_minimum_and_reject_other_roles(self):
        # Read the documented contract independently of the validator constants.
        reference = (SKILL / "references/mapping-rules.md").read_text()
        section = reference.split("## 12. Risk Approval Mapping\n", 1)[1]
        table = section.split("| Role Label", 1)[0]
        matrix = [
            [cell.strip() for cell in line.strip().strip("|").split("|")]
            for line in table.splitlines() if line.startswith("|")
        ]
        treatments = matrix[0][1:]
        roles = ["Not Required", "Product Security", "Lead Security", "CPSO", "Executive"]
        self.assertEqual(len(matrix[2:]), 5)
        self.assertEqual(len(treatments), 4)
        for priority, *minimums in matrix[2:]:
            for treatment, minimum in zip(treatments, minimums):
                for approval in roles:
                    with self.subTest(priority=priority, treatment=treatment, approval=approval):
                        findings = validate(row(**{
                            "State": "Not Applicable" if treatment == "Avoidance" else "Mitigated",
                            "Risk Prioritization": priority,
                            "Risk Treatment": treatment,
                            "Risk Approval": approval,
                        }))
                        if approval == minimum:
                            self.assertEqual(findings, [])
                        else:
                            self.assertEqual(len(findings), 1)
                            finding = findings[0]
                            self.assertEqual(finding.column, "Risk Approval")
                            self.assertEqual(finding.expected, minimum)
                            self.assertEqual(finding.actual, approval)
                            self.assertEqual(finding.row_number, 2)
                            self.assertEqual(finding.threat_id, "42")
                            self.assertEqual(finding.severity, "error")

    def test_blank_and_noncanonical_approvals_fail_for_resolved_inputs(self):
        for approval in ("", "N/A", "None", "cpso", "Security Officer", "CPSO, Executive"):
            with self.subTest(approval=approval):
                findings = validate(row(**{"Risk Approval": approval}))
                self.assertEqual(len(findings), 1)
                self.assertEqual(findings[0].column, "Risk Approval")
                self.assertIn("standardized role label", findings[0].message)

    def test_populated_approval_requires_valid_mapping_inputs(self):
        for column, invalid_values in (
            ("Risk Prioritization", ("", "high", "Severe")),
            ("Risk Treatment", ("", "N/A", "mitigation", "Reduce")),
        ):
            for value in invalid_values:
                with self.subTest(column=column, value=value):
                    findings = validate(row(**{column: value}))
                    self.assertTrue(any(
                        finding.column == column
                        and finding.message.startswith("Risk Approval requires")
                        for finding in findings
                    ))

    def test_na_prioritization_requires_not_required_approval(self):
        for approval in VALIDATOR.RISK_APPROVAL_ROLES:
            with self.subTest(approval=approval):
                findings = validate(row(**{
                    "State": "Not Applicable",
                    "Risk Prioritization": "N/A",
                    "Risk Treatment": "Avoidance",
                    "Risk Approval": approval,
                }))
                if approval == "Not Required":
                    self.assertEqual(findings, [])
                else:
                    self.assertEqual(len(findings), 1)
                    finding = findings[0]
                    self.assertEqual(finding.column, "Risk Approval")
                    self.assertEqual(finding.actual, approval)
                    self.assertEqual(finding.expected, "Not Required")
                    self.assertEqual(finding.row_number, 2)
                    self.assertEqual(finding.threat_id, "42")
                    self.assertEqual(finding.severity, "error")

    def test_incomplete_mapping_inputs_can_retain_blank_approval(self):
        for priority, treatment in (("", ""), ("High", ""), ("", "Mitigation")):
            with self.subTest(priority=priority, treatment=treatment):
                self.assertEqual(VALIDATOR.validate_risk_approval(
                    priority, treatment, "", row_number=2, threat_id="42"
                ), [])

    def test_unresolved_states_require_blank_governance(self):
        for state in ("Not Started", "Needs Investigation"):
            with self.subTest(state=state):
                fields = row(**{
                    "State": state,
                    "Risk Treatment": "",
                    "Risk Approval": "",
                })
                self.assertEqual(validate(fields), [])
                fields["Risk Approval"] = "Executive"
                findings = validate(fields)
                self.assertEqual(len(findings), 1)
                self.assertEqual(findings[0].message, f"{state} requires blank Risk Approval")

    def test_state_treatment_compatibility_still_applies(self):
        findings = validate(row(**{
            "Risk Treatment": "Avoidance",
            "Risk Approval": "Not Required",
        }))
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].message, "Mitigated uses an incompatible treatment")

    def test_short_row_reports_missing_approval_without_crashing(self):
        records = VALIDATOR.parse_records(artifact(row()))
        records[1] = VALIDATOR.Record(records[1].cells[:-1])
        findings = VALIDATOR.validate_rows(records)
        self.assertEqual([finding.column for finding in findings], ["Field count", "Risk Approval"])

    def test_cli_reports_all_rows_and_does_not_modify_input(self):
        source = artifact(
            row(Id="1", **{"Risk Approval": "Product Security"}),
            row(Id="2", **{"Risk Approval": "Executive"}),
            row(Id="3", **{"Risk Approval": "N/A"}),
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "analysis.csv"
            path.write_text(source, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--artifact", str(path)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn("Errors         : 3", result.stdout)
            self.assertIn("output:2 Id 1 [Risk Approval]", result.stdout)
            self.assertIn("output:3 Id 2 [Risk Approval]", result.stdout)
            self.assertIn("output:4 Id 3 [Risk Approval]", result.stdout)
            self.assertIn("- Product Security\n+ CPSO", result.stdout)
            self.assertEqual(path.read_bytes(), source.encode("utf-8"))

    def test_bundled_example_passes_with_source_traceability(self):
        result = subprocess.run(
            [
                sys.executable, str(SCRIPT),
                "--artifact", str(SKILL / "references/Example_Threat_Model_Analysis.csv"),
                "--source", str(SKILL / "references/Example_Threat_Model.csv"),
            ],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("No findings.", result.stdout)


if __name__ == "__main__":
    unittest.main()
