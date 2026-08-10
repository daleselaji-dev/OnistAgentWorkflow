import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class ContractTests(unittest.TestCase):
    def test_all_json_parses(self):
        for path in list((ROOT/'contracts').glob('*.json')) + list((ROOT/'examples').glob('*.json')) + [ROOT/'workflow/workflow.json']:
            with self.subTest(path=path.name): json.loads(path.read_text(encoding='utf-8'))

    def test_reference_examples_present(self):
        names={p.name for p in (ROOT/'examples').glob('*.json')}
        self.assertIn('industrial-3dp-e2e-dry-run.json', names)
        self.assertIn('clo-set-e2e-dry-run.json', names)

    def test_canonical_contracts_present(self):
        required={'canonical-ontology-v1.0.json','cross-stage-handoff-contract-v1.0.json','stage-eval-matrix-v1.0.json','reply-routing-policy-v1.0.json','learning-release-policy-v1.0.json','universe-discovery-policy-v1.0.json'}
        present={p.name for p in (ROOT/'contracts').glob('*.json')}
        self.assertTrue(required <= present)

    def test_handoff_contains_full_spine(self):
        d=json.loads((ROOT/'contracts/cross-stage-handoff-contract-v1.0.json').read_text())
        pairs={(x['from'],x['to']) for x in d['handoffs']}
        expected={('DISCOVERY','EVIDENCE'),('EVIDENCE','QUALIFICATION'),('QUALIFICATION','BUYING_COMMITTEE'),('BUYING_COMMITTEE','PERSUASION'),('PERSUASION','EXECUTION'),('EXECUTION','MEASUREMENT'),('MEASUREMENT','LEARNING')}
        self.assertTrue(expected <= pairs)

    def test_stage_eval_has_all_runtime_stages(self):
        d=json.loads((ROOT/'contracts/stage-eval-matrix-v1.0.json').read_text())
        stages={x['stage'] for x in d['stages']}
        self.assertEqual(stages, {'DISCOVERY','EVIDENCE','QUALIFICATION','BUYING_COMMITTEE','PERSUASION','EXECUTION','MEASUREMENT_LEARNING'})

    def test_no_fake_external_certification_language(self):
        cert=(ROOT/'CERTIFICATION.md').read_text(encoding='utf-8').lower()
        self.assertIn('internal engineering', cert); self.assertIn('not', cert); self.assertIn('third-party', cert)

if __name__ == '__main__': unittest.main()
