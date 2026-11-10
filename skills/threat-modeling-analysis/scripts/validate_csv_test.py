"""Regression tests for threat-model CSV validation."""

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
        "Justification": (
            "Verified controls limit the remaining exposure. EMB3D mitigation assessment: "
            "No applicable TID because the modeled workflow is outside the device boundary."
        ),
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
    def test_all_matrix_cells_allow_minimum_and_escalation_reject_lower_roles(self):
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
                        if roles.index(approval) >= roles.index(minimum):
                            self.assertEqual(findings, [])
                        else:
                            self.assertEqual(len(findings), 1)
                            finding = findings[0]
                            self.assertEqual(finding.column, "Risk Approval")
                            self.assertIn(minimum, finding.expected)
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
            ("Risk Prioritization", ("", "N/A", "high", "Severe")),
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
            self.assertIn("Errors         : 2", result.stdout)
            self.assertIn("output:2 Id 1 [Risk Approval]", result.stdout)
            self.assertIn("output:4 Id 3 [Risk Approval]", result.stdout)
            self.assertIn("- Product Security\n+ CPSO or Executive", result.stdout)
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


class Emb3dAssessmentTests(unittest.TestCase):
    mitigation_index = VALIDATOR.load_emb3d_mitigations(VALIDATOR.DEFAULT_EMB3D_MITIGATIONS)
    citations = (
        "EMB3D Foundational mitigation: System Service Availability Manager (MID-032).",
        "EMB3D Intermediate mitigation: Decidable Protocols and Parsers (MID-008).",
        "EMB3D Leading mitigation: Formally Verified Parsers (MID-088) and "
        "Formal Methods Verification of Critical Functionality Implementation (MID-089).",
    )

    def validate(self, justification, tid="TID-404", state="Mitigated", treatment=None,
                 mitigation_index=None):
        if mitigation_index is None:
            mitigation_index = self.mitigation_index
        if treatment is None:
            treatment = {"Mitigated": "Mitigation", "Not Applicable": "Avoidance"}.get(state, "")
        approval = {"Mitigation": "CPSO", "Acceptance": "CPSO", "Transfer": "CPSO",
                    "Avoidance": "CPSO"}.get(treatment, "")
        fields = row(**{
            "State": state, "EMB3D TID": tid, "Justification": justification,
            "Risk Treatment": treatment, "Risk Approval": approval,
        })
        return VALIDATOR.validate_rows(
            VALIDATOR.parse_records(artifact(fields)), mitigation_index=mitigation_index,
            known_tids=VALIDATOR.load_emb3d_threat_ids(VALIDATOR.DEFAULT_EMB3D_THREATS),
        )

    def test_all_states_require_complete_assessment_and_allow_recommendations(self):
        for state in ("Mitigated", "Not Applicable", "Needs Investigation", "Not Started"):
            with self.subTest(state=state):
                self.assertEqual(self.validate(" ".join(self.citations), state=state), [])
                self.assertEqual(
                    sum("has no disposition" in f.message for f in self.validate("", state=state)),
                    4,
                )
                findings = self.validate(" ".join(self.citations[:2]), state=state)
                self.assertEqual(len(findings), 2)
                self.assertTrue(all("EMB3D Leading mitigation" in f.expected for f in findings))

    def test_other_risk_treatments_do_not_suppress_mitigations(self):
        for treatment in ("Acceptance", "Transfer"):
            with self.subTest(treatment=treatment):
                self.assertEqual(self.validate(" ".join(self.citations), treatment=treatment), [])
                self.assertEqual(len(self.validate("", treatment=treatment)), 4)

    def test_all_distinct_candidates_from_multiple_tids_are_required(self):
        justification = " ".join(self.citations)
        findings = self.validate(justification, tid="TID-404, TID-405")
        self.assertEqual([f.message for f in findings], [
            "Mapped EMB3D mitigation MID-080 has no disposition",
        ])
        self.assertEqual(self.validate(
            justification + " EMB3D mitigation excluded: MID-080 because "
            "the modeled exhaustion occurs before request processing.",
            tid="TID-404, TID-405",
        ), [])

    def test_excluded_and_unresolved_candidates_need_individual_rationales(self):
        justification = " ".join(self.citations[1:])
        for disposition, reason in (
            ("excluded", "independent service recovery cannot address the modeled path"),
            ("unresolved", "the design does not document service restart behavior"),
        ):
            with self.subTest(disposition=disposition):
                prefix = f" EMB3D mitigation {disposition}: MID-032 because "
                self.assertEqual(self.validate(justification + prefix + reason + "."), [])
                self.assertTrue(self.validate(justification + prefix + "."))
        self.assertTrue(self.validate(justification +
            " EMB3D mitigation assessment: No source mapping because no mapping was found."))

    def test_no_candidate_outcomes_are_explicit(self):
        for tid, outcome in (
            ("N/A", "No applicable TID because the modeled path has been removed"),
            ("", "Unresolved because the device architecture is unavailable"),
        ):
            with self.subTest(tid=tid):
                self.assertEqual(len(self.validate("", tid=tid)), 1)
                self.assertEqual(self.validate(
                    f"EMB3D mitigation assessment: {outcome}.", tid=tid
                ), [])
                self.assertTrue(self.validate(
                    "EMB3D mitigation assessment: No source mapping because .", tid=tid
                ))

    def test_known_tid_without_a_mapped_mid_requires_no_source_mapping(self):
        outcome = "EMB3D mitigation assessment: No source mapping because the snapshot lists no MID."
        self.assertEqual(len(self.validate("", mitigation_index={})), 1)
        self.assertEqual(self.validate(outcome, mitigation_index={}), [])
        self.assertTrue(any(
            "absent from the EMB3D threat source" in f.message
            for f in self.validate(outcome, tid="TID-999", mitigation_index={})
        ))

    def test_mid_name_level_identity_and_tid_association(self):
        justification = " ".join(self.citations)
        for original, wrong, diagnostic in (
            ("MID-032", "MID-999", "absent from the EMB3D mitigation source"),
            ("Foundational", "Leading", "level differs"),
            ("System Service Availability Manager", "Service Manager", "exact source name"),
            ("(MID-032)", "(MID-034)", "not mapped to any EMB3D TID"),
        ):
            with self.subTest(wrong=wrong):
                findings = self.validate(justification.replace(original, wrong, 1))
                self.assertTrue(any(diagnostic in f.message for f in findings))

    def test_implementation_requires_device_evidence_and_boundary_clause(self):
        justification = " ".join(self.citations).replace(
            "(MID-032).", "(MID-032) is implemented.", 1
        )
        for prefix in ("", "Compensating controls: Facility watchdog. ",
                       "Implemented controls: Device watchdog. "):
            with self.subTest(prefix=prefix):
                self.assertTrue(any("lacks device-specific evidence" in f.message
                                    for f in self.validate(prefix + justification)))
        evidenced = justification.replace(
            "is implemented.", "is implemented. Device-specific evidence: "
            "Test W-12 verified recovery after watchdog reset.", 1
        )
        self.assertTrue(self.validate("Compensating controls: Facility watchdog. " + evidenced))
        self.assertEqual(self.validate("Implemented controls: Device watchdog. " + evidenced), [])
        self.assertTrue(self.validate(
            "Implemented controls: Device watchdog. " + evidenced.replace(
                "Test W-12 verified recovery after watchdog reset.", "."
            )
        ))


if __name__ == "__main__":
    unittest.main()
