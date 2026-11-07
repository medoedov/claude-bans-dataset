"""Protect the predeclared classification and denominator contracts."""
import unittest
from analyze import calculate, cells, exclusions, outcome, validate_headers


def response(row_id=2, **changes):
    row = dict(row_id=row_id, geography='Россия', tenure='1–6 месяцев',
               payments=['own_named_foreign'], payment_change='Использовал один и тот же',
               vpn_type='Платный коммерческий', vpn_mode='Меняю страны и провайдеров',
               events=['no_problems'], crosscheck={
                   'chat_says_no_claude_ban': False, 'chat_event_answer': False,
                   'chat_works_claude_not': False, 'appeal_answer_present': False,
                   'appeal_submitted': False})
    return dict(row, **changes)


class AnalysisContracts(unittest.TestCase):
    def test_explicit_no_problems_conflicts_with_each_problem_even_ban(self):
        for event in ('ban', 'serial_bans', 'registration_refused', 'payment_refused',
                      'subscription_revoked', 'shadowban', 'other'):
            with self.subTest(event=event):
                self.assertEqual(outcome(response(events=['no_problems', event])), 'contradictory')

    def test_ban_union_has_one_response_and_does_not_require_single_event(self):
        row = response(events=['ban', 'serial_bans', 'payment_refused'])
        self.assertEqual(outcome(row), 'ban_history')
        cell = cells([row])[0]
        self.assertEqual(cell['n'], 1)
        self.assertEqual(cell['ids']['ban_history'], [2])

    def test_either_ban_checkbox_alone_is_sufficient(self):
        rows = [response(2, events=['ban']), response(3, events=['serial_bans'])]
        for row in rows:
            with self.subTest(events=row['events']):
                self.assertEqual(outcome(row), 'ban_history')
        self.assertEqual(cells(rows)[0]['ids']['ban_history'], [2, 3])

    def test_no_problems_must_be_explicit_and_other_problems_are_not_bans(self):
        self.assertEqual(outcome(response(events=[])), 'unknown')
        self.assertEqual(outcome(response()), 'no_problems')
        for event in ('shadowban', 'subscription_revoked', 'other', 'payment_refused'):
            self.assertEqual(outcome(response(events=[event])), 'other_problem')

    def test_multiple_payments_remain_one_exact_set_cell(self):
        row = response(payments=['own_named_foreign', 'gift'])
        data = cells([row, response(3, payments=['gift'])])
        self.assertEqual(sum(c['n'] for c in data), 2)
        combo = next(c for c in data if len(c['payments']) == 2)
        self.assertEqual(combo['ids']['no_problems'], [2])
        self.assertIn('not_exactly_one_defined_paid_method', exclusions(row))

    def test_payment_and_network_are_independent_axes_and_empty_cells_exist(self):
        data = cells([response(), response(3, payments=['reseller'], vpn_type='Свой VPS / собственный сервер')])
        self.assertEqual(len(data), 4)
        self.assertEqual(sum(c['n'] == 0 for c in data), 2)
        self.assertEqual(sum(c['n'] for c in data), 2)

    def test_strict_requires_explicit_unchanged_payment_not_stable_network(self):
        self.assertEqual(exclusions(response()), [])
        for change in (None, 'Менял по другим причинам', 'Менял (был отказ → попробовал другой)'):
            self.assertIn('payment_not_explicitly_unchanged', exclusions(response(payment_change=change)))

    def test_strict_paid_categories_exclude_free_other_missing_and_mixed(self):
        for payment in (['free'], ['other'], [], ['gift', 'free']):
            self.assertIn('not_exactly_one_defined_paid_method', exclusions(response(payments=payment)))
        for payment in ('own_named_foreign', 'virtual_russian_service', 'virtual_foreign_service', 'reseller', 'gift', 'partner'):
            self.assertEqual(exclusions(response(payments=[payment])), [])

    def test_geography_matches_only_explicit_russia(self):
        for geography in (None, 'Другая страна', 'Другая страна СНГ'):
            self.assertIn('not_russia', exclusions(response(geography=geography)))
        self.assertNotIn('not_russia', exclusions(response()))

    def test_calculation_keeps_foreign_answers_out_of_all_russian_tables(self):
        result = calculate({
            'source_url': 'fixture', 'source_sha256': 'fixture',
            'blank_rows': [], 'exact_raw_duplicate_groups': [],
            'rows': [response(2),
                     response(3, geography='Другая страна', events=['ban']),
                     response(4, geography='Другая страна СНГ')]})
        self.assertEqual(result['all']['n'], 3)
        self.assertEqual(result['russia']['ids']['no_problems'], [2])
        self.assertEqual(result['russia']['ids']['ban_history'], [])
        self.assertEqual(result['other_geography']['ids']['ban_history'], [3])
        self.assertEqual(result['other_geography']['ids']['no_problems'], [4])
        for table in ('ru_payment_x_type', 'ru_by_mode', 'ru_by_tenure',
                      'strict_payment_x_type', 'strict_by_mode', 'strict_by_tenure'):
            ids = [i for cell in result[table] for group in cell['ids'].values() for i in group]
            self.assertEqual(ids, [2], table)

    def test_missing_network_and_mode_have_distinct_masks(self):
        self.assertIn('missing_vpn_type', exclusions(response(vpn_type=None)))
        self.assertEqual(exclusions(response(vpn_mode=None)), [])
        self.assertEqual(exclusions(response(vpn_mode=None), True), ['missing_vpn_mode'])
        self.assertEqual(exclusions(response(vpn_type='Не использую')), [])
        self.assertIsNone(cells([response(vpn_type=None)])[0]['vpn_type'])

    def test_outcome_exclusions_are_not_silently_reclassified(self):
        for events in ([], ['shadowban'], ['ban', 'no_problems']):
            self.assertIn('not_two_main_outcomes', exclusions(response(events=events)))

    def test_shifted_headers_fail_even_when_width_stays_same(self):
        expected = [f'column {i}' for i in range(61)]
        actual = expected.copy()
        actual[31], actual[32] = actual[32], actual[31]
        with self.assertRaises(ValueError):
            validate_headers(actual, expected)


if __name__ == '__main__':
    unittest.main()
