import copy
import unittest

from integrate import integrate


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.inputs = dict(
            cases=[dict(case_id="a", outcome="banned", appeal="pending", last_observed_at="2026-10-01", payment_method="own_card_foreign", user_region="NZ")],
            membership=[dict(case_id="a", reasons="rf_document_recorded")],
            details=[dict(case_id="a", details_json='{"document_country":"RU"}')],
            events=[dict(case_id="a", event="kyc_requested")], sources=[],
            new=[dict(candidate_id="new-1", outcome="active", unit="owner_aggregate")],
            dashi={"records": []},
            audit={"episodes": [], "corrections": [], "dedup_decisions": []},
            followups=[dict(case_id="a", event="appeal_rejected", observed_at="2026-11-06")],
            author=dict(case_id="a", outcome="banned", appeal="rejected", reported_on="2026-11-05"),
            decisions=[dict(record_id="a", cohort="confirmed", basis="own Russian passport", unit="account"),
                       dict(record_id="new-1", cohort="probable", existing_case_ids=["a"], action="possible_match", unit="owner_aggregate")],
            extra_corrections=[])

    def test_abroad_inclusion_and_possible_match_do_not_replace_account(self):
        result = integrate(**self.inputs)
        record = result["base_records"][0]
        self.assertEqual(record["inclusion"]["cohort"], "confirmed")
        self.assertEqual(record["case"]["user_region"], "NZ")
        self.assertEqual(record["case"]["outcome"], "banned")
        self.assertEqual(result["new_materials"][0]["unit"], "owner_aggregate")
        self.assertNotIn("unique_accounts", result["summary"])

    def test_followup_keeps_history_and_later_observation(self):
        result = integrate(**self.inputs)
        record = result["base_records"][0]
        self.assertEqual(record["case"]["appeal"], "rejected")
        self.assertEqual(record["case"]["last_observed_at"], "2026-11-06")
        self.assertEqual(record["events"], self.inputs["events"])
        self.assertEqual(len(record["observations"]), 2)

    def test_correction_has_provenance_and_does_not_mutate_input(self):
        self.inputs["extra_corrections"] = [dict(case_id="a", field="payment_method", published_value="own_card_foreign", audited_value="unknown")]
        original = copy.deepcopy(self.inputs)
        result = integrate(**self.inputs)
        record = result["base_records"][0]
        self.assertEqual(record["case"]["payment_method"], "unknown")
        self.assertEqual(record["corrections"][0]["previous_value"], "own_card_foreign")
        self.assertEqual(self.inputs, original)

    def test_stale_correction_is_rejected(self):
        self.inputs["extra_corrections"] = [dict(case_id="a", field="payment_method", published_value="reseller", audited_value="unknown")]
        with self.assertRaisesRegex(ValueError, "precondition"):
            integrate(**self.inputs)

    def test_dangling_links_are_rejected(self):
        self.inputs["decisions"][1]["existing_case_ids"] = ["missing"]
        with self.assertRaisesRegex(ValueError, "Unknown linked"):
            integrate(**self.inputs)

    def test_duplicate_and_unreviewed_materials_are_rejected(self):
        self.inputs["new"].append(copy.deepcopy(self.inputs["new"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            integrate(**self.inputs)
        self.inputs["new"].pop()
        self.inputs["decisions"].pop()
        with self.assertRaisesRegex(ValueError, "Every new material"):
            integrate(**self.inputs)

    def test_unreviewed_candidate_and_its_evidence_are_preserved(self):
        self.inputs["cases"].append(dict(case_id="b", outcome="unknown"))
        self.inputs["membership"].append(dict(case_id="b", reasons="source_group_ru"))
        self.inputs["sources"].append(dict(case_id="b", url="https://example.org/b"))
        result = integrate(**self.inputs)
        records = {r["case"]["case_id"]: r for r in result["base_records"]}
        self.assertEqual(set(records), {"a", "b"})
        self.assertEqual(records["b"]["inclusion"]["cohort"], "unreviewed")
        self.assertEqual(records["b"]["sources"], self.inputs["sources"])
        self.assertEqual(result["summary"]["preserved_candidate_rows"], len(records))

    def test_document_correction_and_aggregate_unit_are_applied(self):
        self.inputs["extra_corrections"] = [
            dict(case_id="a", field="details.document_country", audited_value="unknown"),
            dict(case_id="a", field="unit_of_observation", audited_value="aggregate")]
        result = integrate(**self.inputs)
        record = result["base_records"][0]
        import json
        self.assertEqual(json.loads(record["details"][0]["details_json"])["document_country"], "unknown")
        self.assertEqual(record["corrections"][0]["previous_detail_values"], ["RU"])
        self.assertEqual(record["unit"], "owner_aggregate")

    def test_non_author_appeal_updates_only_the_target_account(self):
        self.inputs["cases"].append(dict(case_id="api", appeal="pending", last_observed_at="2026-11-01"))
        self.inputs["membership"].append(dict(case_id="api", reasons="source_group_ru"))
        self.inputs["followups"][0]["case_id"] = "api"
        result = integrate(**self.inputs)
        records = {r["case"]["case_id"]: r for r in result["base_records"]}
        self.assertEqual(records["api"]["case"]["appeal"], "rejected")
        self.assertEqual(records["api"]["case"]["last_observed_at"], "2026-11-06")
        self.assertEqual(records["a"]["case"]["last_observed_at"], "2026-11-05")


if __name__ == "__main__":
    unittest.main()
