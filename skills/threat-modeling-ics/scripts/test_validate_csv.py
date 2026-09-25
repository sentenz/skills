#!/usr/bin/env python3
"""Regression coverage for risk-treatment and approval validation."""

import unittest

from validate_csv import Cell, EXPECTED_COLUMNS, Record, validate_rows


def governance_findings(
    state="Mitigated",
    priority="Critical",
    treatment="Mitigation",
    approval="Executive",
):
    fields = {
        "Id": "1",
        "State": state,
        "Risk Prioritization": priority,
        "Risk Treatment": treatment,
        "Risk Approval": approval,
        "ATT&CK ID": "N/A",
        "EMB3D TID": "N/A",
        "CWE ID": "N/A",
    }
    header = Record(tuple(Cell(column, False) for column in EXPECTED_COLUMNS))
    record = Record(
        tuple(Cell(fields.get(column, ""), True) for column in EXPECTED_COLUMNS)
    )
    return validate_rows([header, record])


class GovernanceValidationTests(unittest.TestCase):
    def test_approval_thresholds_for_every_actual_treatment(self):
        # These cases express the published approval contract independently of
        # the validator's rank and priority lookup tables.
        roles = (
            "Not Required", "Product Security", "Lead Security", "CPSO", "Executive"
        )
        thresholds = (
            ("Info", 1), ("Low", 1), ("Medium", 2), ("High", 3), ("Critical", 4)
        )
        for treatment in ("Avoidance", "Mitigation", "Acceptance", "Transfer"):
            state = "Not Applicable" if treatment == "Avoidance" else "Mitigated"
            for priority, threshold in thresholds:
                for rank, approval in enumerate(roles):
                    with self.subTest(
                        treatment=treatment, priority=priority, approval=approval
                    ):
                        findings = governance_findings(
                            state, priority, treatment, approval
                        )
                        self.assertEqual(
                            [f.column for f in findings],
                            ["Risk Approval"] if rank < threshold else [],
                        )

    def test_na_requires_no_governance_approval(self):
        self.assertEqual(
            governance_findings("Not Applicable", "Info", "N/A", "Not Required"),
            [],
        )
        for approval in ("Product Security", "Lead Security", "CPSO", "Executive"):
            with self.subTest(approval=approval):
                findings = governance_findings("Not Applicable", "Info", "N/A", approval)
                self.assertEqual([f.column for f in findings], ["Risk Approval"])

    def test_finalized_state_treatment_compatibility(self):
        cases = (
            ("Not Applicable", "Mitigation"),
            ("Not Applicable", "Acceptance"),
            ("Not Applicable", "Transfer"),
            ("Mitigated", "Avoidance"),
            ("Mitigated", "N/A"),
        )
        for state, treatment in cases:
            with self.subTest(state=state, treatment=treatment):
                findings = governance_findings(state=state, treatment=treatment)
                self.assertIn("Risk Treatment", [f.column for f in findings])

    def test_blank_and_unknown_priorities_are_rejected_on_finalized_rows(self):
        for state, treatment, approval in (
            ("Mitigated", "Mitigation", "Product Security"),
            ("Not Applicable", "Avoidance", "Product Security"),
            ("Not Applicable", "N/A", "Not Required"),
        ):
            for priority in ("", "   ", "Critcal", "N/A", "None"):
                with self.subTest(
                    state=state, treatment=treatment, priority=priority
                ):
                    findings = governance_findings(state, priority, treatment, approval)
                    self.assertIn("Risk Prioritization", [f.column for f in findings])

    def test_blank_and_unknown_governance_values_are_rejected(self):
        for treatment in ("", "   ", "Avoid", "Mitigation, Acceptance"):
            with self.subTest(treatment=treatment):
                findings = governance_findings(treatment=treatment)
                self.assertIn("Risk Treatment", [f.column for f in findings])
        for approval in ("", "   ", "CISO", "N/A", "CPSO, Executive"):
            with self.subTest(approval=approval):
                findings = governance_findings(approval=approval)
                self.assertIn("Risk Approval", [f.column for f in findings])

    def test_unresolved_rows_allow_blank_priority_and_governance(self):
        for state in ("Not Started", "Needs Investigation"):
            with self.subTest(state=state):
                self.assertEqual(governance_findings(state, "", "", ""), [])

    def test_unresolved_rows_reject_treatment_and_approval(self):
        for state in ("Not Started", "Needs Investigation"):
            for treatment, approval in (
                ("Mitigation", "Executive"), ("N/A", "Not Required")
            ):
                with self.subTest(state=state, treatment=treatment):
                    findings = governance_findings(state, "", treatment, approval)
                    self.assertEqual(
                        [f.column for f in findings],
                        ["Risk Treatment", "Risk Approval"],
                    )

    def test_blank_and_unknown_states_cannot_bypass_compatibility(self):
        for state in ("", "   ", "Not Appplicable", "mitigated", "Accepted"):
            with self.subTest(state=state):
                findings = governance_findings(state=state, treatment="Avoidance")
                self.assertIn("State", [f.column for f in findings])


if __name__ == "__main__":
    unittest.main()
