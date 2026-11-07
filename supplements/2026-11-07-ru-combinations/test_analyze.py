import unittest
from analyze import analyze, prepare


def corpus(records):
    return {"as_of": "2026-11-07", "defaults": {
        "physical_location": "unknown", "payment": "unknown", "network": "unknown",
        "horizon_7": "insufficient", "horizon_30": "insufficient", "kind": "episode",
        "evidence": "opened", "newness": "reaudit"}, "records": records}


def record(key, **changes):
    return {"id": key, "account": key, "owner": key, "source": "forum", "refs": [key],
            "payment": "card", "network": "vps", "outcome": "active", **changes}


class JointTablesTest(unittest.TestCase):
    def test_payment_and_network_each_split_joint_cells(self):
        result = analyze(corpus([
            record("bank_vps", physical_location="RU", payment="bank", network="vps"),
            record("store_vps", physical_location="RU", payment="store", network="vps", outcome="banned"),
            record("bank_mobile", physical_location="RU", payment="bank", network="mobile"),
            record("bank_vps_later", physical_location="RU", payment="bank", network="vps"),
        ]))
        cells = {(r["payment"], r["network"]): r for r in result["joint_tables"]}
        self.assertEqual(set(cells), {("bank", "vps"), ("store", "vps"), ("bank", "mobile")})
        self.assertEqual(cells[("bank", "vps")]["record_ids"], ["bank_vps", "bank_vps_later"])
        self.assertEqual(cells[("bank", "vps")]["latest_outcomes"], {"active": 2})
        self.assertEqual(cells[("store", "vps")]["latest_outcomes"], {"banned": 1})
        self.assertEqual(cells[("bank", "mobile")]["record_ids"], ["bank_mobile"])

    def test_geography_missing_fields_and_unverified_series_stay_separate(self):
        result = analyze(corpus([
            record("ru", physical_location="RU"), record("unknown"),
            record("abroad", physical_location="abroad"), record("missing", payment="unknown"),
            record("series", kind="series"), record("index", evidence="index_only"),
        ]))
        self.assertEqual({r["physical_location"]: r["record_ids"] for r in result["joint_tables"]},
                         {"RU": ["ru"], "unknown": ["unknown"], "abroad": ["abroad"]})
        self.assertEqual({r["id"] for r in result["excluded_from_joint_table"]}, {"missing", "series", "index"})
        self.assertEqual(result["inventory"]["episode_records"], 4)

    def test_latest_outcome_age_and_post_kyc_do_not_create_horizon_success(self):
        result = analyze(corpus([
            record("alive", account_age_years=2, post_kyc_days=7),
            record("ban", outcome="banned"),
            record("short", horizon_7="worked_through_horizon"),
            record("long", horizon_7="worked_through_horizon", horizon_30="worked_through_horizon"),
            record("early_ban", outcome="banned", horizon_7="ban_by_horizon", horizon_30="ban_by_horizon"),
        ]))
        table = result["joint_tables"][0]
        self.assertEqual(table["horizons"]["30"]["insufficient"], ["alive", "ban", "short"])
        self.assertEqual(table["horizons"]["30"]["worked_through_horizon"], ["long"])
        self.assertEqual(table["horizons"]["7"]["ban_by_horizon"], ["early_ban"])

    def test_shared_accounts_and_owners_are_not_counted_as_independent_people(self):
        result = analyze(corpus([
            record("e1", account="a", owner="o"),
            record("e2", account="a", owner="o", source="second"),
            record("e3", account="b", owner="o"),
        ]))
        self.assertEqual(result["inventory"]["episode_records"], 3)
        self.assertEqual(result["inventory"]["account_keys"], 2)
        self.assertEqual(result["inventory"]["owner_keys"], 1)
        self.assertEqual(result["joint_tables"][0]["owner_keys"], ["o"])
        self.assertEqual(result["without_each_source"]["forum"][0]["record_ids"], ["e2"])
        self.assertEqual(result["without_each_source"]["second"][0]["record_ids"], ["e1", "e3"])

    def test_duplicate_ids_and_invalid_horizons_rejected(self):
        with self.assertRaises(ValueError):
            prepare(corpus([record("x"), record("x")]))
        with self.assertRaises(ValueError):
            prepare(corpus([record("x", horizon_30="safe")]))

    def test_possible_owner_links_remain_visible_without_merging_accounts(self):
        data = corpus([record("a"), record("b")])
        data["possible_owner_links"] = [{"owners": ["a", "b"], "status": "unresolved"}]
        result = analyze(data)
        self.assertEqual(result["possible_owner_links"], data["possible_owner_links"])
        self.assertEqual(result["inventory"]["account_keys"], 2)


if __name__ == "__main__":
    unittest.main()
