import json
import unittest

from select_ru import select, selection_reasons


def case(case_id='test', group='WORLD', location='unknown', notes=''):
    return dict(case_id=case_id, group=group, user_region=location, notes=notes,
                usage_evidence='', cohort='addition', evidence_class='firsthand')


class RussiaSelectionTests(unittest.TestCase):
    def test_world_case_with_russian_document_is_not_lost(self):
        self.assertEqual(selection_reasons(case(), [{'document_country': 'RU'}]), ['rf_document_recorded'])

    def test_all_independent_reasons_survive_together(self):
        row = case(group='RU', location='RU', notes='Паспорт РФ')
        detail = dict(case_id='test', details_json=json.dumps({'document_country': 'RU'}))
        result = select([row], [detail], [], [])
        self.assertEqual(set(result['membership.csv'][0]['reasons'].split(';')),
                         {'source_group_ru', 'location_ru_recorded', 'rf_document_recorded', 'russia_text_mention'})

    def test_source_group_alone_is_only_a_candidate(self):
        result = select([case(group='RU')], [], [], [])
        self.assertEqual(result['membership.csv'][0]['reasons'], 'source_group_ru')
        self.assertEqual(result['membership.csv'][0]['status'], 'candidate_not_citizenship_confirmation')

    def test_rf_substring_in_interface_is_not_russia(self):
        self.assertEqual(selection_reasons(case(notes='Интерфейс не открывается'), []), [])
        self.assertIn('russia_text_mention', selection_reasons(case(notes='Паспорт РФ'), []))

    def test_corrected_document_country_is_not_reintroduced(self):
        self.assertEqual(selection_reasons(case(case_id='v2-0034', notes='российский паспорт'), [{'document_country': 'RU'}]), [])
        result = select([case(case_id='v2-0034', group='RU')], [], [], [])
        self.assertIn('unsupported', result['membership.csv'][0]['known_correction'])

    def test_multiple_details_preserve_one_account_and_all_related_records(self):
        details = [dict(case_id='a', details_json=json.dumps({'document_country': 'RU'})),
                   dict(case_id='a', details_json=json.dumps({'document_type': 'passport'}))]
        events = [dict(case_id='a', event='kyc_requested'), dict(case_id='a', event='banned'),
                  dict(case_id='b', event='active')]
        sources = [dict(case_id='a', url='https://example.org/1'), dict(case_id='b', url='https://example.org/2')]
        result = select([case('a'), case('b')], details, events, sources)
        self.assertEqual([r['case_id'] for r in result['ru-candidates.csv']], ['a'])
        self.assertEqual(result['details.csv'], details)
        self.assertEqual(result['events.csv'], events[:2])
        self.assertEqual(result['sources.csv'], sources[:1])

    def test_recorded_russia_location_in_world_is_included(self):
        self.assertEqual(selection_reasons(case(location='ru'), []), ['location_ru_recorded'])

    def test_related_replacements_are_kept_in_both_directions_transitively(self):
        rows = [case('a', group='RU'), case('b'), case('c')]
        details = [dict(case_id='b', details_json=json.dumps({'related_case_ids': ['a', 'c']}))]
        result = select(rows, details, [], [])
        self.assertEqual([r['case_id'] for r in result['ru-candidates.csv']], ['a', 'b', 'c'])
        self.assertEqual(result['membership.csv'][1]['reasons'], 'related_to_russia_candidate')

    def test_russian_word_in_original_is_a_language_candidate(self):
        self.assertEqual(selection_reasons(case('github-059', notes='В тексте русское слово'), []), ['russian_language_context'])

    def test_missing_linked_id_fails_instead_of_silently_dropping_context(self):
        with self.assertRaisesRegex(ValueError, 'Unknown related account'):
            select([case('a', group='RU')], [dict(case_id='a', details_json=json.dumps({'related_case_ids': ['missing']}))], [], [])


if __name__ == '__main__':
    unittest.main()
