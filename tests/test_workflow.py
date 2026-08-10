import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workflow"))
from runtime import CertifiedWorkflow, WorkflowState, Stage, GateError, demo


class WorkflowTests(unittest.TestCase):
    def make_to_qual(self):
        wf=CertifiedWorkflow(WorkflowState("acct-1","INDUSTRIAL_3DP_BASE"))
        wf.route(["INDUSTRIAL_3DP_BASE"])
        wf.discovery([{"candidate_id":"c1","observed_name":"A"}], True)
        wf.evidence({"account_id":"acct-1","decision_readiness":True})
        return wf

    def test_demo_closes_loop(self):
        result=demo()
        self.assertEqual(result["stage"], "ROUTER")
        self.assertTrue(any(e["type"]=="LEARNING_GATE_PASS" for e in result["events"]))

    def test_candidate_cannot_be_qualified_in_discovery(self):
        wf=CertifiedWorkflow(WorkflowState("acct-1","INDUSTRIAL_3DP_BASE")); wf.route(["INDUSTRIAL_3DP_BASE"])
        with self.assertRaises(GateError): wf.discovery([{"candidate_id":"c1","qualified_label":True}], True)

    def test_open_world_completeness_required(self):
        wf=CertifiedWorkflow(WorkflowState("acct-1","INDUSTRIAL_3DP_BASE")); wf.route(["INDUSTRIAL_3DP_BASE"])
        with self.assertRaises(GateError): wf.discovery([{"candidate_id":"c1"}], False)

    def test_wrong_entity_merge_fails(self):
        wf=CertifiedWorkflow(WorkflowState("acct-1","INDUSTRIAL_3DP_BASE")); wf.route(["INDUSTRIAL_3DP_BASE"]); wf.discovery([{"candidate_id":"c1"}], True)
        with self.assertRaises(GateError): wf.evidence({"account_id":"acct-1","decision_readiness":True,"wrong_entity_merge":True})

    def test_hard_gate_rejects(self):
        wf=self.make_to_qual(); wf.qualify({"account_id":"acct-1","hard_gates":{"technical_envelope":"FAIL"},"action_class":"PRIORITIZE_OUTBOUND"})
        self.assertEqual(wf.state.stage, Stage.REJECT); self.assertEqual(wf.state.action_class, "REJECT_ADAPTER")

    def test_uncalibrated_probability_fails(self):
        wf=self.make_to_qual()
        with self.assertRaises(GateError): wf.qualify({"account_id":"acct-1","hard_gates":{},"action_class":"PRIORITIZE_OUTBOUND","purchase_probability":0.82})

    def test_borrowed_roi_fails(self):
        wf=self.make_to_qual(); wf.qualify({"account_id":"acct-1","hard_gates":{},"action_class":"PRIORITIZE_OUTBOUND"}); wf.buying_committee({"target_contact_id":"p1"})
        with self.assertRaises(GateError): wf.persuasion({"facts":[],"hypotheses":[],"mechanisms":[],"proofs":[],"questions":[],"proposal":"x","borrowed_roi":True})

    def test_unknown_jurisdiction_holds(self):
        wf=self.make_to_qual(); wf.qualify({"account_id":"acct-1","hard_gates":{},"action_class":"PRIORITIZE_OUTBOUND"}); wf.buying_committee({"target_contact_id":"p1"}); wf.persuasion({"facts":[],"hypotheses":[],"mechanisms":[],"proofs":[],"questions":[],"proposal":"x"}); wf.execute({"jurisdiction_resolved":False,"suppressed":False,"approved":True})
        self.assertEqual(wf.state.stage, Stage.HOLD); self.assertIn("JURISDICTION_UNKNOWN", wf.state.hold_reason)

    def test_uncertain_send_never_blind_retries(self):
        wf=self.make_to_qual(); wf.qualify({"account_id":"acct-1","hard_gates":{},"action_class":"PRIORITIZE_OUTBOUND"}); wf.buying_committee({"target_contact_id":"p1"}); wf.persuasion({"facts":[],"hypotheses":[],"mechanisms":[],"proofs":[],"questions":[],"proposal":"x"}); wf.execute({"jurisdiction_resolved":True,"suppressed":False,"approved":True,"provider_result":"UNCERTAIN"})
        self.assertEqual(wf.state.stage, Stage.HOLD); self.assertEqual(wf.state.hold_reason, "FAILED_UNCERTAIN_RECONCILE")

    def test_c0_cannot_promote_performance_policy(self):
        wf=self.make_to_qual(); wf.qualify({"account_id":"acct-1","hard_gates":{},"action_class":"PRIORITIZE_OUTBOUND"}); wf.buying_committee({"target_contact_id":"p1"}); wf.persuasion({"facts":[],"hypotheses":[],"mechanisms":[],"proofs":[],"questions":[],"proposal":"x"}); wf.execute({"jurisdiction_resolved":True,"suppressed":False,"approved":True,"provider_result":"SUCCESS"}); wf.measure({"data_quality":"PASS","attribution_claimed_as_causal":False})
        with self.assertRaises(GateError): wf.learn({"update_class":"PERSUASION_OR_SEQUENCE_OPTIMIZATION","causal_grade":"C0","global_policy_change":True,"rollback_target":"v0","guardrails":"PASS"})


if __name__ == "__main__": unittest.main()
