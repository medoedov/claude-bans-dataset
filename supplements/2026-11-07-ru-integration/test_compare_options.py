import unittest

from compare_options import PRIMARY, analyze, compare, fisher, holm, prepare, wilson


def row(cid, network, outcome, component=None, prior=False):
    return dict(case_id=cid, access_ip=network, outcome=outcome, component=component or cid,
                age_bin="unknown", confirmed_prior_ban=prior)


class ComparisonTests(unittest.TestCase):
    def test_separate_outcomes_and_unknown_factor(self):
        rows = [row("a", "datacenter_vps", "banned"), row("b", "datacenter_vps", "active"),
                row("c", "datacenter_vps", "kyc_prompt"), row("d", "commercial_vpn", "locked"),
                row("e", "commercial_vpn", "survived"), row("f", "unknown", "banned")]
        result = compare(rows, PRIMARY["network"])
        self.assertEqual((result["a"]["banned"], result["a"]["n"]), (1, 2))
        self.assertEqual((result["b"]["banned"], result["b"]["n"]), (0, 1))
        self.assertEqual(result["a"]["outcomes"]["kyc_prompt"], 1)
        self.assertEqual(result["missing_or_other_factor"], 1)
        locked = compare(rows, PRIMARY["network"], "banned_or_locked")
        self.assertEqual((locked["b"]["banned"], locked["b"]["n"]), (1, 2))

    def test_component_representative_chosen_across_both_sides(self):
        rows = [row("z", "datacenter_vps", "banned", "owner"),
                row("a", "commercial_vpn", "active", "owner"),
                row("0", "unknown", "active", "owner")]
        result = compare(rows, PRIMARY["network"], one_per_component=True)
        self.assertEqual(result["known_rows"], 1)
        self.assertEqual(result["b"]["active_ids"], ["a"])
        self.assertEqual(result["a"]["n"], 0)

    def test_prior_ban_sensitivity_does_not_double_count_active(self):
        rows = [row("a", "datacenter_vps", "active", prior=True),
                row("b", "datacenter_vps", "unbanned", prior=True),
                row("c", "datacenter_vps", "unbanned", prior=False),
                row("d", "commercial_vpn", "active")]
        current = compare(rows, PRIMARY["network"])
        prior = compare(rows, PRIMARY["network"], "documented_prior_ban")
        self.assertEqual((current["a"]["banned"], current["a"]["n"]), (0, 1))
        self.assertEqual((prior["a"]["banned"], prior["a"]["active"], prior["a"]["n"]), (2, 0, 2))

    def test_fisher_known_table_and_symmetry(self):
        self.assertAlmostEqual(fisher(1, 9, 11, 3), 0.0027594561852200836)
        self.assertAlmostEqual(fisher(11, 3, 1, 9), fisher(1, 9, 11, 3))
        self.assertAlmostEqual(fisher(5, 5, 5, 5), 1)

    def test_wilson_edges_and_holm_family(self):
        self.assertIsNone(wilson(0, 0))
        self.assertAlmostEqual(wilson(0, 10)[1], 0.2775327998628892)
        self.assertAlmostEqual(wilson(10, 10)[0], 1 - wilson(0, 10)[1])
        self.assertEqual(holm({"a": 0.01, "b": 0.04, "c": 0.03, "d": None}),
                         {"a": 0.04, "c": 0.09, "b": 0.09, "d": None})

    def test_population_overrides_missing_age_and_product_exclusions(self):
        def record(cid, cohort="legacy", product="unknown", unit="unreviewed_case_row"):
            return dict(case=dict(case_id=cid, plan="pro", product=product, cohort=cohort,
                                  evidence_class="firsthand", user_region="RU", source="habr",
                                  url="https://habr.com/ru/articles/1/comments/#comment_2", account_age_months="unknown"),
                        unit=unit, details=[], events=[])
        data = dict(base_records=[record("a"), record("b"), record("c", "addition"),
                                  record("d", product="console_api"), record("e", unit="owner_aggregate")], review_decisions=[])
        rows, excluded = prepare(data, dict(overrides=[dict(case_id="a", fields=dict(user_region="UZ"))], dependency_links=[["a", "b"]]))
        result = {r["case_id"]: r for r in rows}
        self.assertEqual(set(result), {"a", "b"})
        self.assertEqual(result["a"]["location"], "known_abroad")
        self.assertEqual(result["b"]["location"], "recorded_RU")
        self.assertEqual(result["a"]["age_bin"], "unknown")
        self.assertEqual(result["a"]["component"], result["b"]["component"])
        self.assertEqual({r["case_id"] for r in excluded}, {"c", "d", "e"})

    def test_disjoint_alternatives_and_empty_cells(self):
        with self.assertRaisesRegex(ValueError, "overlap"):
            compare([], ("access_ip", {"x"}, {"x"}))
        result = compare([row("a", "datacenter_vps", "banned")], PRIMARY["network"])
        self.assertIsNone(result["fisher_p"])
        self.assertIsNone(result["difference_pp"])

    def test_analysis_filters_collections_strata_and_holm_family(self):
        def sample(cid, location, collection, network, plan, outcome, thread):
            r = row(cid, network, outcome)
            r.update(location=location, collection=collection, plan=plan, plan_bin="max20" if plan == "max20" else "pro_max5",
                     usage="heavy" if plan == "max20" else "normal", payment_method="own_card_foreign" if network == "datacenter_vps" else "reseller",
                     ip_stable="yes", source_family="habr", thread=thread, product="consumer", wave="2026-10-01", late_observation="no")
            return r
        rows = [sample("a", "recorded_RU", "legacy", "datacenter_vps", "max20", "banned", "t1"),
                sample("b", "recorded_RU", "legacy", "commercial_vpn", "pro", "active", "t1"),
                sample("c", "recorded_RU", "addition", "datacenter_vps", "pro", "active", "t2"),
                sample("d", "recorded_RU", "addition", "commercial_vpn", "max20", "banned", "t2"),
                sample("e", "unknown_location", "legacy", "datacenter_vps", "max20", "active", "t3"),
                sample("f", "known_abroad", "addition", "datacenter_vps", "max20", "banned", "t3")]
        tables = analyze(rows)
        def get(population="recorded_RU", collection="all", view="all", comparison="network"):
            return next(r for r in tables if (r["population"], r["collection"], r["view"], r["comparison"]) == (population, collection, view, comparison))
        self.assertEqual(get()["a"]["ban_ids"], ["a"])
        self.assertEqual(get()["a"]["active_ids"], ["c"])
        self.assertEqual(get("context_compatible")["a"]["active_ids"], ["c", "e"])
        self.assertEqual(get("context_compatible")["a"]["ban_ids"], ["a"])
        self.assertEqual(get(collection="legacy")["a"]["n"], 1)
        self.assertEqual(get(collection="addition")["a"]["ban_ids"], [])
        self.assertEqual(get(view="plan_bin=max20")["a"]["active_ids"], [])
        self.assertEqual(get(view="without_largest_thread")["a"]["active_ids"], ["c"])
        self.assertEqual(get(view="without_largest_thread")["a"]["ban_ids"], [])
        corrected = [r for r in tables if "holm_p_four_primary" in r]
        self.assertEqual({r["comparison"] for r in corrected}, set(PRIMARY))
        self.assertEqual(len(corrected), 4)
        self.assertTrue(all(r["population"] == "recorded_RU" and r["collection"] == "all" and r["view"] == "all" for r in corrected))
        self.assertEqual({r["comparison"]: r["holm_p_four_primary"] for r in corrected},
                         holm({r["comparison"]: r["fisher_p"] for r in corrected}))
        self.assertGreater(get(comparison="plan")["holm_p_four_primary"], get(comparison="plan")["fisher_p"])
        self.assertEqual(get(view="without_largest_thread", comparison="appstore_vs_reseller")["comparison"], "appstore_vs_reseller")
        self.assertEqual(get(view="plan_bin=pro_max5", comparison="appstore_vs_reseller")["b"]["active_ids"], ["b"])
        self.assertEqual(get(view="source=habr", comparison="appstore_vs_reseller")["b"]["ban_ids"], ["d"])

    def test_preparation_reads_events_and_both_dependency_sources(self):
        def record(cid, details=None, events=None):
            return dict(case=dict(case_id=cid, plan="pro", product="consumer", cohort="addition", evidence_class="firsthand", user_region="RU",
                                  source="habr", url="", account_age_months="", outcome="unbanned"),
                        unit="account", details=details or [], events=events or [])
        data = dict(base_records=[record("a", [dict(details_json='{"related_case_ids":["b"]}')], [dict(event="banned")]),
                                  record("b"), record("c")],
                    review_decisions=[dict(existing_case_ids=["b", "c"])])
        rows, _ = prepare(data, dict(overrides=[]))
        self.assertEqual(len({r["component"] for r in rows}), 1)
        self.assertEqual([r["case_id"] for r in rows if r["confirmed_prior_ban"]], ["a"])


if __name__ == "__main__":
    unittest.main()
