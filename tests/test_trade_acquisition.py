"""Certification tests for the trade-acquisition loop extension.

Covers: contract integrity, channel-draft compliance gates, follow-up /
meeting state-machine legality, cadence discipline, discovery/evidence
benchmarks, loop repeatability, and learning-release guardrails.
"""
import json
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "workflow"))

from runtime import GateError  # noqa: E402
from acquisition import (  # noqa: E402
    AcquisitionLoopRunner,
    ChannelDraftGate,
    FollowUpStateMachine,
    check_policy_promotion,
    demo,
    evaluate_discovery_benchmark,
    evaluate_evidence_completeness,
    score_timing_triggers,
)

BENCHMARK = json.loads((ROOT / "examples" / "trade-acquisition-benchmark.json").read_text(encoding="utf-8"))
CHANNEL_POLICY = json.loads((ROOT / "contracts" / "outreach-channel-policy-v1.0.json").read_text(encoding="utf-8"))
STATE_MACHINE = json.loads((ROOT / "contracts" / "followup-meeting-state-machine-v1.0.json").read_text(encoding="utf-8"))
TRIGGERS = json.loads((ROOT / "contracts" / "timing-trigger-taxonomy-v1.0.json").read_text(encoding="utf-8"))


def good_email_draft(**overrides):
    draft = {
        "channel": "EMAIL",
        "touch_number": 1,
        "subject": "Fixture lead time at Nordwerk",
        "body": "Hi Ms. Keller — saw your posting for an additive engineer. "
                "Are fixture lead times gating line changeovers? If useful, "
                "I can review one live fixture workflow with you in 20 minutes.",
        "value_packet_ref": "vhp-test-001",
        "fact_claim_ids": ["claim-hiring-001"],
        "sender_identity_disclosed": True,
        "opt_out_affordance": True,
    }
    draft.update(overrides)
    return draft


def start_sequence(machine, **overrides):
    kwargs = dict(
        account_id="acct-t1", adapter_id="INDUSTRIAL_3DP_BASE",
        person_id="p1", role="PROBLEM_OWNER", value_packet_ref="vhp-test-001",
    )
    kwargs.update(overrides)
    return machine.start(**kwargs)


def send_first_touch(machine, seq, channel="EMAIL"):
    return machine.advance(
        seq, "send_approved", day=0,
        draft_status="DRAFT_READY", approved=True, jurisdiction_resolved=True, channel=channel,
    )


class ContractIntegrityTests(unittest.TestCase):
    def test_new_contracts_present_and_versioned(self):
        for name in (
            "outreach-channel-policy-v1.0.json",
            "followup-meeting-state-machine-v1.0.json",
            "timing-trigger-taxonomy-v1.0.json",
        ):
            data = json.loads((ROOT / "contracts" / name).read_text(encoding="utf-8"))
            self.assertEqual(data["version"], "v1.0", name)

    def test_channel_policy_covers_all_required_channels(self):
        for channel in ("EMAIL", "LINKEDIN", "WHATSAPP"):
            rules = CHANNEL_POLICY["channels"][channel]
            self.assertTrue(rules.get("tone"), channel)
            self.assertTrue(rules.get("frequency"), channel)
            self.assertTrue(rules.get("compliance", {}).get("requires"), channel)
        self.assertTrue(CHANNEL_POLICY["forbidden_patterns"])
        self.assertEqual(
            CHANNEL_POLICY["value_packet_binding"]["sections"],
            ["FACT", "HYPOTHESIS", "MECHANISM", "PROOF", "QUESTION", "PROPOSAL"],
        )

    def test_state_machine_states_transitions_consistent(self):
        states = set(STATE_MACHINE["states"])
        required = {
            "DRAFT_READY", "SENT", "OPENED", "NO_REPLY", "FOLLOWUP_1", "FOLLOWUP_2",
            "FOLLOWUP_3", "HUMAN_TAKEOVER", "MEETING_PROPOSED", "MEETING_BOOKED",
            "MEETING_CONFIRMED", "MEETING_HELD", "QUALIFIED_OPPORTUNITY", "NURTURE",
            "CLOSED_LOST", "HOLD", "UNSUBSCRIBED",
        }
        self.assertTrue(required <= states)
        for t in STATE_MACHINE["transitions"]:
            self.assertIn(t["from"], states)
            self.assertIn(t["to"], states)
        for i in STATE_MACHINE["global_interrupts"]:
            self.assertIn(i["to"], states)
        terminal = {s for s, spec in STATE_MACHINE["states"].items() if spec["kind"].startswith("terminal")}
        for t in STATE_MACHINE["transitions"]:
            self.assertNotIn(t["from"], terminal, f"terminal state {t['from']} must have no outgoing transition")

    def test_cadence_touch_plan_matches_max_touches(self):
        cadence = STATE_MACHINE["cadence"]
        self.assertEqual(len(cadence["touch_plan"]), cadence["max_touches_per_sequence"])
        offsets = [t["day_offset"] for t in cadence["touch_plan"]]
        self.assertEqual(offsets, sorted(offsets))
        for prev, cur in zip(offsets, offsets[1:]):
            self.assertGreaterEqual(cur - prev, cadence["min_interval_days"])

    def test_trigger_taxonomy_families_complete(self):
        families = {t["id"] for t in TRIGGERS["trigger_families"]}
        required = {
            "HIRING_SIGNAL", "EXPANSION", "TRADE_SHOW", "REGULATORY", "TECH_STACK_SHIFT",
            "COMPETITOR_MOVE", "FUNDING_CAPEX", "LEADERSHIP_CHANGE", "SUPPLY_CHAIN_EVENT",
            "NEW_PRODUCT_LAUNCH",
        }
        self.assertEqual(families, required)
        for t in TRIGGERS["trigger_families"]:
            self.assertGreater(t["freshness_window_days"], 0)
            self.assertGreater(t["priority_weight"], 0)
            self.assertTrue(t["min_evidence"])


class ChannelDraftGateTests(unittest.TestCase):
    def setUp(self):
        self.gate = ChannelDraftGate()

    def test_benchmark_draft_fixtures_behave_as_labeled(self):
        for fixture in BENCHMARK["draft_fixtures"]:
            with self.subTest(fixture=fixture["fixture_id"]):
                if fixture["expected_gate"] == "PASS":
                    verdict = self.gate.validate(fixture["draft"])
                    self.assertEqual(verdict["status"], "DRAFT_READY")
                else:
                    with self.assertRaises(GateError) as ctx:
                        self.gate.validate(fixture["draft"])
                    self.assertIn(fixture["expected_reason_substring"], str(ctx.exception))

    def test_draft_requires_value_packet_ref(self):
        with self.assertRaises(GateError):
            self.gate.validate(good_email_draft(value_packet_ref=None))

    def test_numeric_roi_promise_blocked(self):
        draft = good_email_draft(body="We can save you 30% on tooling costs immediately.")
        with self.assertRaises(GateError) as ctx:
            self.gate.validate(draft)
        self.assertIn("ROI_NUMERIC_PROMISE", str(ctx.exception))

    def test_person_intent_assumption_blocked(self):
        draft = good_email_draft(body="I know you are looking for a 3D printing supplier right now.")
        with self.assertRaises(GateError) as ctx:
            self.gate.validate(draft)
        self.assertIn("PERSON_INTENT_ASSUMPTION", str(ctx.exception))

    def test_unknown_timezone_blocks_scheduling(self):
        draft = good_email_draft(scheduled_local_time="09:30", recipient_timezone_known=False)
        with self.assertRaises(GateError) as ctx:
            self.gate.validate(draft)
        self.assertIn("timezone", str(ctx.exception))

    def test_email_requires_opt_out_affordance(self):
        with self.assertRaises(GateError):
            self.gate.validate(good_email_draft(opt_out_affordance=False))


class FollowUpStateMachineTests(unittest.TestCase):
    def setUp(self):
        self.machine = FollowUpStateMachine()

    def test_happy_path_reaches_qualified_opportunity(self):
        seq = start_sequence(self.machine)
        send_first_touch(self.machine, seq)
        self.machine.advance(seq, "no_reply_window_elapsed", day=3)
        self.machine.advance(seq, "followup_due", day=3, channel="EMAIL")
        self.machine.advance(seq, "reply_substantive", day=5)
        self.machine.advance(seq, "classified_meeting_interest", day=5)
        self.machine.advance(seq, "slot_accepted", day=6)
        self.machine.advance(seq, "confirmation_pack_complete", day=7, confirmation_pack={
            f: True for f in STATE_MACHINE["confirmation_pack_fields"]
        })
        self.machine.advance(seq, "meeting_held", day=8)
        self.machine.advance(seq, "outcome_qualified", day=8, debrief={
            f: "recorded" for f in STATE_MACHINE["debrief_fields"]
        })
        self.assertEqual(seq["state"], "QUALIFIED_OPPORTUNITY")

    def test_substantive_reply_pauses_automation(self):
        seq = start_sequence(self.machine)
        send_first_touch(self.machine, seq)
        self.machine.advance(seq, "reply_substantive", day=1)
        self.assertEqual(seq["state"], "HUMAN_TAKEOVER")
        self.assertTrue(seq["automation_paused"])
        with self.assertRaises(GateError):
            self.machine.advance(seq, "followup_due", day=10, channel="EMAIL")

    def test_followup_min_interval_enforced(self):
        seq = start_sequence(self.machine)
        send_first_touch(self.machine, seq)
        self.machine.advance(seq, "no_reply_window_elapsed", day=1)
        with self.assertRaises(GateError) as ctx:
            self.machine.advance(seq, "followup_due", day=1, channel="EMAIL")
        self.assertIn("minimum interval", str(ctx.exception))

    def test_max_touches_enforced_by_construction(self):
        seq = start_sequence(self.machine)
        send_first_touch(self.machine, seq)
        self.machine.advance(seq, "no_reply_window_elapsed", day=3)
        self.machine.advance(seq, "followup_due", day=3, channel="EMAIL")
        self.machine.advance(seq, "followup_due", day=7, channel="EMAIL")
        self.machine.advance(seq, "followup_due", day=14, channel="EMAIL")
        self.assertEqual(seq["state"], "FOLLOWUP_3")
        with self.assertRaises(GateError):
            self.machine.advance(seq, "followup_due", day=20, channel="EMAIL")

    def test_channel_switch_needs_prior_touches(self):
        seq = start_sequence(self.machine, connection_accepted=True)
        send_first_touch(self.machine, seq)
        self.machine.advance(seq, "no_reply_window_elapsed", day=3)
        with self.assertRaises(GateError) as ctx:
            self.machine.advance(seq, "followup_due", day=3, channel="LINKEDIN")
        self.assertIn("channel switch", str(ctx.exception).lower())

    def test_whatsapp_touch_requires_consent(self):
        seq = start_sequence(self.machine)
        send_first_touch(self.machine, seq)
        self.machine.advance(seq, "no_reply_window_elapsed", day=3)
        self.machine.advance(seq, "followup_due", day=3, channel="EMAIL")
        with self.assertRaises(GateError) as ctx:
            self.machine.advance(seq, "followup_due", day=7, channel="WHATSAPP")
        self.assertIn("consent", str(ctx.exception))

    def test_whatsapp_cold_first_touch_blocked_at_send(self):
        seq = start_sequence(self.machine)
        with self.assertRaises(GateError):
            self.machine.advance(
                seq, "send_approved", day=0,
                draft_status="DRAFT_READY", approved=True, jurisdiction_resolved=True,
                channel="WHATSAPP",
            )

    def test_send_requires_gated_draft_and_approval(self):
        seq = start_sequence(self.machine)
        with self.assertRaises(GateError):
            self.machine.advance(seq, "send_approved", day=0, approved=True, jurisdiction_resolved=True, channel="EMAIL")
        with self.assertRaises(GateError):
            self.machine.advance(seq, "send_approved", day=0, draft_status="DRAFT_READY", jurisdiction_resolved=True, channel="EMAIL")

    def test_meeting_confirmation_pack_required(self):
        seq = start_sequence(self.machine)
        send_first_touch(self.machine, seq)
        self.machine.advance(seq, "reply_substantive", day=2)
        self.machine.advance(seq, "classified_meeting_interest", day=2)
        self.machine.advance(seq, "slot_accepted", day=3)
        with self.assertRaises(GateError) as ctx:
            self.machine.advance(seq, "confirmation_pack_complete", day=4, confirmation_pack={"agenda_one_liner": "x"})
        self.assertIn("confirmation pack incomplete", str(ctx.exception))

    def test_meeting_debrief_required_before_outcome(self):
        seq = start_sequence(self.machine)
        send_first_touch(self.machine, seq)
        self.machine.advance(seq, "reply_substantive", day=2)
        self.machine.advance(seq, "classified_meeting_interest", day=2)
        self.machine.advance(seq, "slot_accepted", day=3)
        self.machine.advance(seq, "confirmation_pack_complete", day=4, confirmation_pack={
            f: True for f in STATE_MACHINE["confirmation_pack_fields"]
        })
        self.machine.advance(seq, "meeting_held", day=5)
        with self.assertRaises(GateError):
            self.machine.advance(seq, "outcome_qualified", day=5, debrief={})

    def test_reschedule_cap_enforced(self):
        seq = start_sequence(self.machine)
        send_first_touch(self.machine, seq)
        self.machine.advance(seq, "reply_substantive", day=2)
        self.machine.advance(seq, "classified_meeting_interest", day=2)
        pack = {f: True for f in STATE_MACHINE["confirmation_pack_fields"]}
        for day in (3, 5):
            self.machine.advance(seq, "slot_accepted", day=day)
            self.machine.advance(seq, "confirmation_pack_complete", day=day, confirmation_pack=pack)
            self.machine.advance(seq, "no_show", day=day + 1)
        self.machine.advance(seq, "slot_accepted", day=8)
        self.machine.advance(seq, "confirmation_pack_complete", day=8, confirmation_pack=pack)
        with self.assertRaises(GateError) as ctx:
            self.machine.advance(seq, "no_show", day=9)
        self.assertIn("reschedule cap", str(ctx.exception))

    def test_opt_out_is_terminal_suppression(self):
        seq = start_sequence(self.machine)
        send_first_touch(self.machine, seq)
        self.machine.advance(seq, "opt_out", day=1)
        self.assertEqual(seq["state"], "UNSUBSCRIBED")
        self.assertTrue(seq["suppressed"])
        with self.assertRaises(GateError):
            self.machine.advance(seq, "followup_due", day=10, channel="EMAIL")

    def test_illegal_transition_rejected(self):
        seq = start_sequence(self.machine)
        with self.assertRaises(GateError):
            self.machine.advance(seq, "slot_accepted", day=0)

    def test_person_switch_requires_distinct_role_and_cap(self):
        seq = start_sequence(self.machine)
        send_first_touch(self.machine, seq)
        self.machine.advance(seq, "no_reply_window_elapsed", day=3)
        self.machine.advance(seq, "followup_due", day=3, channel="EMAIL")
        self.machine.advance(seq, "followup_due", day=7, channel="EMAIL")
        self.machine.advance(seq, "followup_due", day=14, channel="EMAIL")
        self.machine.advance(seq, "sequence_exhausted", day=17)
        self.assertEqual(seq["state"], "NURTURE")
        with self.assertRaises(GateError):
            self.machine.switch_person(seq, "p2", "PROBLEM_OWNER", "sequence_exhausted_no_engagement")
        fresh = self.machine.switch_person(seq, "p2", "ECONOMIC_BUYER", "sequence_exhausted_no_engagement")
        self.assertEqual(fresh["state"], "DRAFT_READY")
        self.assertEqual(fresh["person_switches"], 1)
        with self.assertRaises(GateError):
            self.machine.switch_person(seq, "p3", "TECHNICAL_EVALUATOR", "random_reason")


class TimingAndBenchmarkTests(unittest.TestCase):
    def test_timing_cases_from_benchmark(self):
        for case in BENCHMARK["timing_cases"]:
            with self.subTest(case=case["case_id"]):
                result = score_timing_triggers(case["triggers"], case["today"])
                self.assertEqual(result["recommendation"], case["expected_recommendation"])

    def test_undated_trigger_cannot_activate(self):
        with self.assertRaises(GateError):
            score_timing_triggers([{"trigger_id": "HIRING_SIGNAL", "evidence_ref": "claim-x"}], 0)
        with self.assertRaises(GateError):
            score_timing_triggers([{"trigger_id": "HIRING_SIGNAL", "observed_day": -5}], 0)

    def test_discovery_benchmark_recall_and_diversity(self):
        result = evaluate_discovery_benchmark(BENCHMARK["discovery_benchmark"])
        self.assertTrue(result["pass"])
        self.assertGreaterEqual(result["recall"], 0.75)
        self.assertGreaterEqual(result["source_family_count"], 4)
        self.assertFalse(result["open_world_complete"])

    def test_discovery_completeness_claim_forbidden(self):
        fixture = dict(BENCHMARK["discovery_benchmark"])
        fixture["open_world_complete_claimed"] = True
        with self.assertRaises(GateError):
            evaluate_discovery_benchmark(fixture)

    def test_evidence_completeness_fixtures(self):
        required = BENCHMARK["evidence_completeness"]["required_claims"]
        for ledger in BENCHMARK["evidence_completeness"]["ledgers"]:
            with self.subTest(ledger=ledger["ledger_id"]):
                result = evaluate_evidence_completeness(ledger, required)
                self.assertEqual(result["complete"], ledger["expected_complete"])
                if not ledger["expected_complete"]:
                    self.assertEqual(result["missing"], ledger["expected_missing"])


class LoopAndLearningTests(unittest.TestCase):
    def test_loop_runs_all_rounds_and_is_repeatable(self):
        first = AcquisitionLoopRunner().run(BENCHMARK)
        second = AcquisitionLoopRunner().run(BENCHMARK)
        self.assertEqual(first["result_hash"], second["result_hash"])
        self.assertEqual(len(first["rounds"]), 3)
        totals = first["rounds"][0]["totals"]
        self.assertGreaterEqual(totals["qualified"], 1)
        self.assertGreaterEqual(totals["violations_blocked"], 1)

    def test_cadence_violation_probe_is_blocked_not_silent(self):
        result = AcquisitionLoopRunner().run_round(BENCHMARK["loop_rounds"][0])
        probe_thread = next(t for t in result["threads"] if t["thread_id"] == "r1-clo-nurture-with-probe")
        self.assertEqual(probe_thread["metrics"]["violations_blocked"], 1)
        self.assertEqual(probe_thread["final_state"], "NURTURE")

    def test_single_success_cannot_promote_global_policy(self):
        with self.assertRaises(GateError) as ctx:
            check_policy_promotion({
                "update_class": "PERSUASION_OR_SEQUENCE_OPTIMIZATION",
                "scope": "BROAD",
                "causal_grade": "C0",
                "offline_eval_pass": True,
                "guardrails": "PASS",
                "rollback_target": "policy-v1.0",
            })
        self.assertIn("C3", str(ctx.exception))

    def test_c3_canary_with_gates_allowed(self):
        verdict = check_policy_promotion({
            "update_class": "PERSUASION_OR_SEQUENCE_OPTIMIZATION",
            "scope": "CANARY",
            "causal_grade": "C3",
            "offline_eval_pass": True,
            "guardrails": "PASS",
            "rollback_target": "policy-v1.0",
        })
        self.assertTrue(verdict["allowed"])

    def test_broad_persuasion_rollout_requires_replication(self):
        with self.assertRaises(GateError) as ctx:
            check_policy_promotion({
                "update_class": "PERSUASION_OR_SEQUENCE_OPTIMIZATION",
                "scope": "BROAD",
                "causal_grade": "C3",
                "offline_eval_pass": True,
                "guardrails": "PASS",
                "rollback_target": "policy-v1.0",
                "replicated": False,
            })
        self.assertIn("replicated", str(ctx.exception))

    def test_account_fact_update_stays_in_account_memory(self):
        verdict = check_policy_promotion({
            "update_class": "ACCOUNT_FACT_UPDATE", "scope": "ACCOUNT_MEMORY", "causal_grade": "C0",
        })
        self.assertTrue(verdict["allowed"])
        with self.assertRaises(GateError):
            check_policy_promotion({
                "update_class": "ACCOUNT_FACT_UPDATE", "scope": "BROAD", "causal_grade": "C0",
            })

    def test_guardrail_failure_blocks_promotion(self):
        with self.assertRaises(GateError):
            check_policy_promotion({
                "update_class": "ROUTING_OR_RANKING_OPTIMIZATION",
                "scope": "CANARY",
                "causal_grade": "C2",
                "offline_eval_pass": True,
                "guardrails": "FAIL",
                "rollback_target": "policy-v1.0",
            })

    def test_integrated_demo_reaches_qualified_and_closes_spine_loop(self):
        result = demo()
        self.assertEqual(result["sequence_final_state"], "QUALIFIED_OPPORTUNITY")
        self.assertEqual(result["spine"]["stage"], "ROUTER")
        self.assertEqual(result["timing"]["recommendation"], "OUTBOUND_NOW")
        self.assertEqual(result["draft_gate"]["status"], "DRAFT_READY")


if __name__ == "__main__":
    unittest.main()
