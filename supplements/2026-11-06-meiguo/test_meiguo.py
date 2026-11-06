import unittest

from analyze_meiguo import km_curve, summarize, survival_at


class SurvivalTests(unittest.TestCase):
    def test_censoring_and_ties(self):
        # Four subjects: one censored at 1; event and censor at 2; event at 3.
        curve = km_curve([(1, False), (2, True), (2, False), (3, True)])
        self.assertEqual(curve[0]['at_risk'], 3)
        self.assertAlmostEqual(survival_at(curve, 2), 2 / 3)
        self.assertEqual(survival_at(curve, 3), 0)
        self.assertEqual(survival_at(curve, 1.9), 1)

    def test_simultaneous_events(self):
        curve = km_curve([(2, True), (2, True), (2, False), (4, False)])
        self.assertEqual(curve[0]['events'], 2)
        self.assertEqual(survival_at(curve, 2), 0.5)

    def test_mature_cohort_includes_early_bans_excludes_recent_ones(self):
        rows = [dict(age_hours=72, duration_hours=1, event=True),
                dict(age_hours=72, duration_hours=72, event=False),
                dict(age_hours=24, duration_hours=1, event=True)]
        result = summarize(rows, 48)
        self.assertEqual((result['mature_n'], result['mature_events']), (2, 1))
        self.assertEqual(result['mature_fraction'], 0.5)
        self.assertIsNone(result['km_survival'])  # risk-set threshold

    def test_rounding_sensitivity_and_exact_boundary(self):
        rows = [dict(age_hours=49, duration_hours=48.5, event=True),
                dict(age_hours=48.5, duration_hours=48.5, event=False)]
        base, shifted = summarize(rows, 48), summarize(rows, 48, 1)
        self.assertEqual((base['mature_n'], base['mature_events']), (2, 0))
        self.assertEqual((shifted['mature_n'], shifted['mature_events']), (1, 1))

    def test_supported_horizon_reports_survival_not_risk(self):
        rows = [dict(age_hours=72, duration_hours=1, event=True)]
        rows += [dict(age_hours=72, duration_hours=72, event=False) for _ in range(11)]
        result = summarize(rows, 48)
        self.assertEqual(result['at_risk'], 11)
        self.assertAlmostEqual(result['km_survival'], 11 / 12)
        self.assertAlmostEqual(result['mature_fraction'], 1 / 12)


if __name__ == '__main__':
    unittest.main()
