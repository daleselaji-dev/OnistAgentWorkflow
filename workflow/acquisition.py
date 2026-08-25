#!/usr/bin/env python3
"""Deterministic dry-run extension for the trade-acquisition loop.

Refines PERSUASION -> EXECUTION -> MEASUREMENT into:
channel-draft gates + follow-up / meeting sub-state machine + timing-trigger
scoring + repeatable benchmark loop. All rules are data-driven from
contracts/*.json so the contracts stay the single source of truth.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from runtime import CertifiedWorkflow, GateError, WorkflowState, stable_hash

ROOT = Path(__file__).resolve().parents[1]
CHANNEL_POLICY_PATH = ROOT / "contracts" / "outreach-channel-policy-v1.0.json"
STATE_MACHINE_PATH = ROOT / "contracts" / "followup-meeting-state-machine-v1.0.json"
TRIGGER_TAXONOMY_PATH = ROOT / "contracts" / "timing-trigger-taxonomy-v1.0.json"
LEARNING_POLICY_PATH = ROOT / "contracts" / "learning-release-policy-v1.0.json"

GRADE_ORDER = {"C0": 0, "C1": 1, "C2": 2, "C3": 3, "C4": 4}
PLACEHOLDER_RE = re.compile(r"\{\{[^{}]*\}\}")
LINK_RE = re.compile(r"https?://")


def load_contract(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_hhmm(value: str) -> int:
    hours, minutes = value.split(":")
    return int(hours) * 60 + int(minutes)


class ChannelDraftGate:
    """Deterministic renderer gate: a draft violating channel policy never reaches DRAFT_READY."""

    def __init__(self, policy: Optional[Dict[str, Any]] = None):
        self.policy = policy or load_contract(CHANNEL_POLICY_PATH)

    def validate(self, draft: Dict[str, Any]) -> Dict[str, Any]:
        channel = draft.get("channel")
        channels = self.policy["channels"]
        if channel not in channels:
            raise GateError(f"unknown channel: {channel}")
        if not draft.get("value_packet_ref"):
            raise GateError("draft must reference a frozen ValueHypothesisPacket (value_packet_ref)")
        if not draft.get("fact_claim_ids"):
            raise GateError("draft FACT sentence must be traceable to evidence claim ids (fact_claim_ids)")

        subject = draft.get("subject", "")
        body = draft.get("body", "")
        text = f"{subject}\n{body}"
        if PLACEHOLDER_RE.search(text):
            raise GateError("unresolved placeholder blocks DRAFT_READY")
        for pattern in self.policy["forbidden_patterns"]:
            if re.search(pattern["regex"], text):
                raise GateError(f"forbidden pattern {pattern['id']}: {pattern['reason']}")

        touch_number = draft.get("touch_number", 1)
        first_on_channel = draft.get("first_on_channel", touch_number == 1)
        links = len(LINK_RE.findall(body))
        words = len(body.split())
        rules = channels[channel]

        if channel == "EMAIL":
            limits = rules["first_touch"] if touch_number == 1 else rules["followup_touch"]
            if touch_number == 1 and len(subject) > rules["first_touch"]["max_subject_chars"]:
                raise GateError("email subject exceeds channel limit")
            if words > limits["max_body_words"]:
                raise GateError("email body exceeds channel word limit")
            if links > limits["max_links"]:
                raise GateError("email exceeds link limit")
            if not draft.get("sender_identity_disclosed"):
                raise GateError("email requires disclosed sender identity")
            if not draft.get("opt_out_affordance"):
                raise GateError("email requires an opt-out affordance")
        elif channel == "LINKEDIN":
            message_type = draft.get("message_type", "message")
            if message_type == "connection_note":
                if len(body) > rules["connection_note"]["max_chars"]:
                    raise GateError("linkedin connection note exceeds char limit")
                if links > rules["connection_note"]["max_links"]:
                    raise GateError("linkedin connection note cannot carry links")
            else:
                if not draft.get("connection_accepted"):
                    raise GateError("linkedin message requires accepted connection")
                if len(body) > rules["message"]["max_chars"]:
                    raise GateError("linkedin message exceeds char limit")
                if first_on_channel and links > rules["message"]["links_in_first_message"]:
                    raise GateError("first linkedin message cannot carry links")
        elif channel == "WHATSAPP":
            if not draft.get("consent_verified"):
                raise GateError("whatsapp requires consent or existing business relationship")
            if words > rules["message"]["max_words"] or len(body) > rules["message"]["max_chars"]:
                raise GateError("whatsapp message exceeds length limit")
            if first_on_channel and links > rules["message"]["links_in_first_message"]:
                raise GateError("first whatsapp message cannot carry links")

        scheduled = draft.get("scheduled_local_time")
        if scheduled is not None:
            if not draft.get("recipient_timezone_known"):
                raise GateError("unknown recipient timezone blocks scheduling")
            window = rules.get("send_window_local")
            if window:
                minute = _parse_hhmm(scheduled)
                if not (_parse_hhmm(window["start"]) <= minute <= _parse_hhmm(window["end"])):
                    raise GateError("scheduled send time outside channel local window")

        return {"status": "DRAFT_READY", "channel": channel, "draft_hash": stable_hash(draft)}


class FollowUpStateMachine:
    """Contract-driven follow-up / meeting sub-state machine for one outreach thread."""

    def __init__(self, contract: Optional[Dict[str, Any]] = None):
        self.contract = contract or load_contract(STATE_MACHINE_PATH)
        self.states: Dict[str, Dict[str, Any]] = self.contract["states"]
        self.transitions: Dict[tuple, Dict[str, Any]] = {
            (t["from"], t["event"]): t for t in self.contract["transitions"]
        }
        self.interrupts: Dict[str, Dict[str, Any]] = {
            i["event"]: i for i in self.contract["global_interrupts"]
        }
        self.cadence = self.contract["cadence"]

    def start(
        self,
        account_id: str,
        adapter_id: str,
        person_id: str,
        role: str,
        value_packet_ref: str,
        consent_whatsapp: bool = False,
        connection_accepted: bool = False,
    ) -> Dict[str, Any]:
        return {
            "sequence_id": f"seq-{account_id}-{adapter_id}-{person_id}",
            "account_id": account_id,
            "adapter_id": adapter_id,
            "person_id": person_id,
            "role": role,
            "value_packet_ref": value_packet_ref,
            "state": "DRAFT_READY",
            "day": 0,
            "touches": [],
            "consent_whatsapp": consent_whatsapp,
            "connection_accepted": connection_accepted,
            "automation_paused": False,
            "suppressed": False,
            "reschedules": 0,
            "person_switches": 0,
            "persons_history": [{"person_id": person_id, "role": role}],
            "history": [],
        }

    def advance(self, seq: Dict[str, Any], event: str, day: Optional[int] = None, **payload: Any) -> Dict[str, Any]:
        state = seq["state"]
        kind = self.states[state]["kind"]
        if kind.startswith("terminal"):
            raise GateError(f"terminal state {state} accepts no further events")
        if day is None:
            day = seq["day"]
        if day < seq["day"]:
            raise GateError("sequence time cannot move backwards")
        seq["day"] = day

        if event in self.interrupts:
            target = self.interrupts[event]["to"]
            if event == "reply_substantive":
                seq["automation_paused"] = True
            if event == "opt_out":
                seq["suppressed"] = True
            self._record(seq, state, event, target, day)
            seq["state"] = target
            return seq

        transition = self.transitions.get((state, event))
        if transition is None:
            raise GateError(f"illegal transition: {state} --{event}--> ?")
        guard = transition.get("guard")
        if guard:
            getattr(self, f"_guard_{guard}")(seq, day, payload)

        target = transition["to"]
        if self.states[target]["kind"] == "touch":
            channel = payload.get("channel", "EMAIL")
            seq["touches"].append({"touch": len(seq["touches"]) + 1, "day": day, "channel": channel})
        if event == "resume_automation":
            seq["automation_paused"] = False
        if event == "reschedule_requested" or event == "no_show":
            seq["reschedules"] += 1
        self._record(seq, state, event, target, day)
        seq["state"] = target
        return seq

    def switch_person(self, seq: Dict[str, Any], new_person_id: str, new_role: str, reason: str) -> Dict[str, Any]:
        rules = self.cadence["person_switch_rules"]
        if reason not in rules["allowed_after"]:
            raise GateError(f"person switch reason not allowed: {reason}")
        expected_state = "NURTURE" if reason == "sequence_exhausted_no_engagement" else "HOLD"
        if seq["state"] != expected_state:
            raise GateError(f"person switch for {reason} requires state {expected_state}")
        if rules["requires_distinct_buying_role"] and new_role == seq["role"]:
            raise GateError("person switch requires a distinct buying role")
        if seq["person_switches"] >= rules["max_person_switches_per_account_product_90d"]:
            raise GateError("person switch cap reached for account x product")
        fresh = self.start(
            seq["account_id"], seq["adapter_id"], new_person_id, new_role, seq["value_packet_ref"]
        )
        fresh["person_switches"] = seq["person_switches"] + 1
        fresh["persons_history"] = seq["persons_history"] + [{"person_id": new_person_id, "role": new_role}]
        fresh["day"] = seq["day"]
        return fresh

    # --- guards -----------------------------------------------------------
    def _channel_access_check(self, seq: Dict[str, Any], channel: str) -> None:
        if channel not in self.contract["channels"]:
            raise GateError(f"unknown channel: {channel}")
        if channel == "WHATSAPP" and not seq.get("consent_whatsapp"):
            raise GateError("WhatsApp touch requires consent or existing business relationship")
        if channel == "LINKEDIN" and not seq.get("connection_accepted"):
            raise GateError("LinkedIn message requires an accepted connection")

    def _guard_execution_gate_pass(self, seq: Dict[str, Any], day: int, payload: Dict[str, Any]) -> None:
        if seq["automation_paused"]:
            raise GateError("automation paused; sends forbidden until human classification")
        if seq["suppressed"]:
            raise GateError("suppressed contact cannot be messaged")
        if payload.get("draft_status") != "DRAFT_READY":
            raise GateError("send requires a draft that passed the channel gate")
        if not payload.get("approved"):
            raise GateError("send requires human/policy approval")
        if not payload.get("jurisdiction_resolved"):
            raise GateError("unknown jurisdiction blocks send")
        self._channel_access_check(seq, payload.get("channel", "EMAIL"))

    def _guard_cadence_ok(self, seq: Dict[str, Any], day: int, payload: Dict[str, Any]) -> None:
        if seq["automation_paused"]:
            raise GateError("automation paused; follow-up touches forbidden until human classification")
        if seq["suppressed"]:
            raise GateError("suppressed contact cannot be messaged")
        touches = seq["touches"]
        if len(touches) >= self.cadence["max_touches_per_sequence"]:
            raise GateError("max touches per sequence exceeded")
        channel = payload.get("channel")
        if not channel:
            raise GateError("follow-up touch requires an explicit channel")
        last_day = touches[-1]["day"] if touches else None
        if last_day is not None and day - last_day < self.cadence["min_interval_days"]:
            raise GateError("follow-up earlier than minimum interval")
        used = {t["channel"] for t in touches}
        min_prior = self.cadence["channel_switch_rules"]["switch_to_new_channel_requires_prior_touches"]
        if channel not in used and len(touches) < min_prior:
            raise GateError("channel switch requires giving the first channel enough touches")
        self._channel_access_check(seq, channel)

    def _guard_confirmation_pack_fields(self, seq: Dict[str, Any], day: int, payload: Dict[str, Any]) -> None:
        pack = payload.get("confirmation_pack") or {}
        missing = [f for f in self.contract["confirmation_pack_fields"] if not pack.get(f)]
        if missing:
            raise GateError(f"confirmation pack incomplete: {missing}")

    def _guard_reschedule_cap(self, seq: Dict[str, Any], day: int, payload: Dict[str, Any]) -> None:
        if seq["reschedules"] >= self.cadence["max_reschedules"]:
            raise GateError("reschedule cap reached")

    def _guard_debrief_complete(self, seq: Dict[str, Any], day: int, payload: Dict[str, Any]) -> None:
        debrief = payload.get("debrief") or {}
        missing = [f for f in self.contract["debrief_fields"] if not debrief.get(f)]
        if missing:
            raise GateError(f"meeting debrief incomplete: {missing}")

    def _guard_reminder_sent_once(self, seq: Dict[str, Any], day: int, payload: Dict[str, Any]) -> None:
        if not payload.get("reminder_sent"):
            raise GateError("exactly one reminder must be sent before abandoning a meeting proposal")

    def _record(self, seq: Dict[str, Any], state: str, event: str, target: str, day: int) -> None:
        seq["history"].append({"day": day, "from": state, "event": event, "to": target})


def score_timing_triggers(
    active_triggers: List[Dict[str, Any]], today: int, taxonomy: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Trigger-first targeting: score = sum(weight x freshness) over dated, evidence-backed triggers."""
    taxonomy = taxonomy or load_contract(TRIGGER_TAXONOMY_PATH)
    families = {t["id"]: t for t in taxonomy["trigger_families"]}
    score = 0.0
    active: List[str] = []
    for trigger in active_triggers:
        family = families.get(trigger.get("trigger_id"))
        if family is None:
            raise GateError(f"unknown trigger family: {trigger.get('trigger_id')}")
        if trigger.get("observed_day") is None or not trigger.get("evidence_ref"):
            raise GateError("an undated or unevidenced trigger cannot activate outbound")
        age = today - trigger["observed_day"]
        if 0 <= age <= family["freshness_window_days"]:
            score += family["priority_weight"]
            active.append(family["id"])
    activation = taxonomy["activation"]
    if score >= activation["min_score_outbound_now"]:
        recommendation = "OUTBOUND_NOW"
    elif score >= 0.5:
        recommendation = "DISCOVERY_OUTREACH"
    else:
        recommendation = "MONITOR_NURTURE"
    return {"score": round(score, 4), "active_triggers": active, "recommendation": recommendation}


def evaluate_discovery_benchmark(fixture: Dict[str, Any]) -> Dict[str, Any]:
    """Recall vs known positives + source-family diversity; completeness claims are forbidden."""
    if fixture.get("open_world_complete_claimed"):
        raise GateError("open-world discovery cannot claim completeness")
    known = set(fixture["known_positives"])
    retrieved = fixture["retrieved_candidates"]
    retrieved_ids = {c["candidate_id"] for c in retrieved}
    recall = len(known & retrieved_ids) / len(known) if known else 0.0
    families = {c["source_family"] for c in retrieved}
    targets = fixture["targets"]
    recall_ok = recall >= targets["min_recall"]
    diversity_ok = len(families) >= targets["min_source_families"]
    return {
        "recall": round(recall, 4),
        "source_family_count": len(families),
        "recall_target_met": recall_ok,
        "diversity_target_met": diversity_ok,
        "pass": recall_ok and diversity_ok,
        "open_world_complete": False,
    }


def evaluate_evidence_completeness(ledger: Dict[str, Any], required_claims: List[str]) -> Dict[str, Any]:
    """A decision-ready company dossier needs every required claim SUPPORTED with a source."""
    claims = ledger.get("claims", {})
    missing = []
    for claim_id in required_claims:
        claim = claims.get(claim_id)
        if not claim or claim.get("status") != "SUPPORTED" or not claim.get("source"):
            missing.append(claim_id)
    return {"ledger_id": ledger.get("ledger_id"), "complete": not missing, "missing": missing}


def check_policy_promotion(update: Dict[str, Any], policy: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Learning gate: single-run success can never promote a global performance policy."""
    policy = policy or load_contract(LEARNING_POLICY_PATH)
    update_class = update.get("update_class")
    config = policy["update_classes"].get(update_class)
    if config is None:
        raise GateError(f"unknown update class: {update_class}")
    scope = update.get("scope", "BROAD")
    grade = GRADE_ORDER.get(update.get("causal_grade", "C0"), 0)

    if update_class == "ACCOUNT_FACT_UPDATE" and scope != "ACCOUNT_MEMORY":
        raise GateError("account fact updates cannot exceed account memory scope")
    if update_class == "EVAL_DATASET_CORRECTION" and scope != "EVAL_DATASET":
        raise GateError("eval corrections cannot exceed eval dataset scope")

    if scope in {"CANARY", "BROAD"}:
        if update_class in {"ACCOUNT_FACT_UPDATE", "EVAL_DATASET_CORRECTION"}:
            raise GateError("this update class cannot touch production policy")
        if update_class == "SAFETY_CORRECTNESS_FIX":
            if not update.get("offline_eval_pass") or not update.get("human_review") or not update.get("rollback_target"):
                raise GateError("safety fix requires offline eval, human review, and rollback target")
        else:
            key = "minimum_causal_grade_for_canary" if scope == "CANARY" else "minimum_causal_grade_for_broad_promotion"
            if grade < GRADE_ORDER[config[key]]:
                raise GateError(
                    f"{update_class} at {scope} requires >= {config[key]}; "
                    "single-case success is C0 and cannot promote a global policy"
                )
            if not update.get("offline_eval_pass"):
                raise GateError("offline eval pass required before promotion")
            if update.get("guardrails") != "PASS":
                raise GateError("guardrail failure blocks promotion")
            if not update.get("rollback_target"):
                raise GateError("production policy change requires a rollback target")
            if update_class == "PERSUASION_OR_SEQUENCE_OPTIMIZATION" and scope == "BROAD" and not update.get("replicated"):
                raise GateError("broad persuasion/sequence rollout requires replicated evidence")
    return {"allowed": True, "update_class": update_class, "scope": scope}


class AcquisitionLoopRunner:
    """Repeatable dry-run benchmark loop over scripted fixture rounds."""

    def __init__(self, machine: Optional[FollowUpStateMachine] = None, gate: Optional[ChannelDraftGate] = None):
        self.machine = machine or FollowUpStateMachine()
        self.gate = gate or ChannelDraftGate()

    def run_thread(self, thread: Dict[str, Any]) -> Dict[str, Any]:
        seq = self.machine.start(
            account_id=thread["account_id"],
            adapter_id=thread["adapter_id"],
            person_id=thread["person_id"],
            role=thread["role"],
            value_packet_ref=thread["value_packet_ref"],
            consent_whatsapp=thread.get("consent_whatsapp", False),
            connection_accepted=thread.get("connection_accepted", False),
        )
        metrics = {
            "touches_sent": 0, "replies": 0, "meetings_booked": 0, "meetings_held": 0,
            "qualified": 0, "nurture": 0, "closed_lost": 0, "unsubscribed": 0, "violations_blocked": 0,
        }
        for step in thread["steps"]:
            event = step["event"]
            payload = dict(step.get("payload", {}))
            if "draft" in payload:
                verdict = self.gate.validate(payload.pop("draft"))
                payload.setdefault("draft_status", verdict["status"])
                payload.setdefault("channel", verdict["channel"])
                payload.setdefault("approved", True)
                payload.setdefault("jurisdiction_resolved", True)
            try:
                self.machine.advance(seq, event, day=step.get("day"), **payload)
            except GateError:
                if step.get("expect_blocked"):
                    metrics["violations_blocked"] += 1
                    continue
                raise
            if step.get("expect_blocked"):
                raise GateError(f"step expected to be blocked but passed: {event}")
        metrics["touches_sent"] = len(seq["touches"])
        metrics["replies"] = sum(1 for h in seq["history"] if h["event"] == "reply_substantive")
        metrics["meetings_booked"] = sum(1 for h in seq["history"] if h["to"] == "MEETING_BOOKED")
        metrics["meetings_held"] = sum(1 for h in seq["history"] if h["to"] == "MEETING_HELD")
        metrics["qualified"] = 1 if seq["state"] == "QUALIFIED_OPPORTUNITY" else 0
        metrics["nurture"] = 1 if seq["state"] == "NURTURE" else 0
        metrics["closed_lost"] = 1 if seq["state"] == "CLOSED_LOST" else 0
        metrics["unsubscribed"] = 1 if seq["state"] == "UNSUBSCRIBED" else 0
        return {"thread_id": thread["thread_id"], "final_state": seq["state"], "metrics": metrics}

    def run_round(self, round_fixture: Dict[str, Any]) -> Dict[str, Any]:
        thread_results = [self.run_thread(t) for t in round_fixture["threads"]]
        totals: Dict[str, int] = {}
        for result in thread_results:
            for key, value in result["metrics"].items():
                totals[key] = totals.get(key, 0) + value
        return {"round_id": round_fixture["round_id"], "threads": thread_results, "totals": totals}

    def run(self, benchmark: Dict[str, Any]) -> Dict[str, Any]:
        rounds = [self.run_round(r) for r in benchmark["loop_rounds"]]
        return {"rounds": rounds, "result_hash": stable_hash({"rounds": rounds})}


def demo() -> Dict[str, Any]:
    """Integrated dry-run: certified spine + acquisition sub-machine to QUALIFIED_OPPORTUNITY."""
    wf = CertifiedWorkflow(WorkflowState(account_id="acct-demo-trade", product_adapter_id="INDUSTRIAL_3DP_BASE"))
    wf.route(["INDUSTRIAL_3DP_BASE"])
    wf.discovery([{"candidate_id": "cand-trade-1", "observed_name": "Nordwerk Automotive Fixtures"}], True)
    wf.evidence({
        "account_id": "acct-demo-trade",
        "decision_readiness": True,
        "claims": ["hiring additive engineer", "fixture outsourcing observed", "DACH plant expansion"],
    })
    timing = score_timing_triggers(
        [
            {"trigger_id": "HIRING_SIGNAL", "observed_day": -10, "evidence_ref": "claim-hiring-001"},
            {"trigger_id": "EXPANSION", "observed_day": -40, "evidence_ref": "claim-expansion-002"},
        ],
        today=0,
    )
    wf.qualify({
        "account_id": "acct-demo-trade",
        "hard_gates": {"technical_envelope": "PASS", "jurisdiction_zone": "PASS"},
        "action_class": "PRIORITIZE_OUTBOUND" if timing["recommendation"] == "OUTBOUND_NOW" else "DISCOVERY_OUTREACH",
    })
    wf.buying_committee({"target_contact_id": "person-me-lead", "roles": ["PROBLEM_OWNER"]})
    wf.persuasion({
        "facts": ["job post for additive engineer (claim-hiring-001)", "fixture outsourcing observed (claim-fixture-003)"],
        "hypotheses": ["if fixtures are outsourced, iteration may wait on external queues"],
        "mechanisms": ["in-house additive tooling can shorten fixture turnaround"],
        "proofs": ["external automotive case: weeks-to-days fixture lead time (possibility, not promise)"],
        "questions": ["are fixture lead times currently gating line changeovers?"],
        "proposal": "20-minute review of one live fixture workflow",
        "borrowed_roi": False,
    })

    gate = ChannelDraftGate()
    draft = {
        "channel": "EMAIL",
        "touch_number": 1,
        "subject": "Fixture lead time at Nordwerk",
        "body": (
            "Hi Ms. Keller — saw your posting for an additive manufacturing engineer for the Stuttgart line. "
            "If your jigs and fixtures are still outsourced, iteration may be waiting on external machine-shop queues. "
            "Teams in automotive tooling have moved fixture turnaround from weeks to days by printing in-house; "
            "whether that mechanism applies depends on your part mix. "
            "Are fixture lead times currently gating line changeovers? "
            "If useful, I can walk through one of your live fixture workflows in 20 minutes."
        ),
        "value_packet_ref": "vhp-demo-trade-001",
        "fact_claim_ids": ["claim-hiring-001", "claim-fixture-003"],
        "sender_identity_disclosed": True,
        "opt_out_affordance": True,
        "scheduled_local_time": "09:30",
        "recipient_timezone_known": True,
    }
    verdict = gate.validate(draft)
    wf.execute({
        "jurisdiction_resolved": True, "suppressed": False, "approved": True,
        "owner_collision": False, "provider_result": "SUCCESS", "channel": "EMAIL",
    })

    machine = FollowUpStateMachine()
    seq = machine.start("acct-demo-trade", "INDUSTRIAL_3DP_BASE", "person-me-lead", "PROBLEM_OWNER", "vhp-demo-trade-001")
    machine.advance(seq, "send_approved", day=0, draft_status=verdict["status"], approved=True, jurisdiction_resolved=True, channel="EMAIL")
    machine.advance(seq, "no_reply_window_elapsed", day=3)
    machine.advance(seq, "followup_due", day=3, channel="EMAIL")
    machine.advance(seq, "reply_substantive", day=5)
    machine.advance(seq, "classified_meeting_interest", day=5)
    machine.advance(seq, "slot_accepted", day=6)
    machine.advance(seq, "confirmation_pack_complete", day=7, confirmation_pack={
        "agenda_one_liner": "review one live fixture workflow",
        "attendee_roles_both_sides": "ME lead + our applications engineer",
        "recipient_timezone_confirmed": "Europe/Berlin",
        "duration_minutes": 20,
        "dial_in_or_location": "video call",
        "evidence_summary_ref": "evidence-brief-001",
        "t24h_reconfirm_scheduled": True,
    })
    machine.advance(seq, "meeting_held", day=8)
    machine.advance(seq, "outcome_qualified", day=8, debrief={
        "notes_to_evidence_ledger": "fixture lead time 3 weeks confirmed by problem owner",
        "reply_classification": "PAIN_CONFIRMED",
        "next_action": "technical evaluation with sample part",
    })

    wf.measure({"data_quality": "PASS", "attribution_claimed_as_causal": False, "outcome": "QUALIFIED_OPPORTUNITY"})
    wf.learn({"update_class": "ACCOUNT_FACT_UPDATE", "causal_grade": "C0", "global_policy_change": False, "guardrails": "PASS"})

    return {
        "spine": wf.state.snapshot(),
        "timing": timing,
        "draft_gate": verdict,
        "sequence_final_state": seq["state"],
        "sequence_history": seq["history"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()
    if args.demo:
        print(json.dumps(demo(), indent=2, ensure_ascii=False))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
