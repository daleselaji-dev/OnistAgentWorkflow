#!/usr/bin/env python3
"""Deterministic dry-run reference runtime for Onist Account-to-Opportunity workflow."""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class Stage(str, Enum):
    ROUTER = "ROUTER"
    DISCOVERY = "DISCOVERY"
    EVIDENCE = "EVIDENCE"
    QUALIFICATION = "QUALIFICATION"
    BUYING_COMMITTEE = "BUYING_COMMITTEE"
    PERSUASION = "PERSUASION"
    EXECUTION = "EXECUTION"
    MEASUREMENT = "MEASUREMENT"
    LEARNING = "LEARNING"
    HOLD = "HOLD"
    REJECT = "REJECT"
    PAUSED = "PAUSED"


@dataclass
class WorkflowState:
    account_id: str
    product_adapter_id: str
    stage: Stage = Stage.ROUTER
    action_class: str | None = None
    hold_reason: str | None = None
    artifact_refs: Dict[str, str] = field(default_factory=dict)
    events: List[Dict[str, Any]] = field(default_factory=list)

    def snapshot(self) -> Dict[str, Any]:
        return {
            "account_id": self.account_id,
            "product_adapter_id": self.product_adapter_id,
            "stage": self.stage.value,
            "action_class": self.action_class,
            "hold_reason": self.hold_reason,
            "artifact_refs": self.artifact_refs,
            "events": self.events,
        }


class GateError(ValueError):
    pass


def stable_hash(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


class CertifiedWorkflow:
    """State/gate reference implementation; external side effects are simulated."""

    def __init__(self, state: WorkflowState):
        self.state = state

    def route(self, adapter_ids: List[str]) -> WorkflowState:
        if self.state.product_adapter_id not in adapter_ids:
            raise GateError("selected product adapter is not supported by router output")
        self._event("ROUTER_PASS", {"adapters": adapter_ids})
        self.state.stage = Stage.DISCOVERY
        return self.state

    def discovery(self, candidates: List[Dict[str, Any]], open_world_flag: bool = True) -> WorkflowState:
        if self.state.stage != Stage.DISCOVERY:
            raise GateError("discovery called out of order")
        if not open_world_flag:
            raise GateError("open-world candidate discovery must preserve not-complete semantics")
        if not candidates:
            self.state.stage = Stage.HOLD
            self.state.hold_reason = "NO_CANDIDATES_OR_SOURCE_GAP"
            return self.state
        for c in candidates:
            if c.get("qualified_label"):
                raise GateError("candidate discovery cannot emit qualified labels")
        self._event("DISCOVERY_PASS", {"candidate_count": len(candidates)})
        self.state.stage = Stage.EVIDENCE
        return self.state

    def evidence(self, ledger: Dict[str, Any]) -> WorkflowState:
        if self.state.stage != Stage.EVIDENCE:
            raise GateError("evidence called out of order")
        if ledger.get("account_id") != self.state.account_id:
            raise GateError("account identity continuity failure")
        if ledger.get("wrong_entity_merge"):
            raise GateError("wrong entity merge")
        if ledger.get("unsupported_decision_claim"):
            raise GateError("unsupported decision-bearing claim")
        if ledger.get("not_found_treated_as_negative"):
            raise GateError("not-found cannot be treated as verified negative")
        if not ledger.get("decision_readiness", False):
            self.state.stage = Stage.HOLD
            self.state.hold_reason = "EVIDENCE_NOT_READY"
            return self.state
        self.state.artifact_refs["evidence"] = stable_hash(ledger)
        self._event("EVIDENCE_PASS", {"ledger_hash": self.state.artifact_refs["evidence"]})
        self.state.stage = Stage.QUALIFICATION
        return self.state

    def qualify(self, decision: Dict[str, Any]) -> WorkflowState:
        if self.state.stage != Stage.QUALIFICATION:
            raise GateError("qualification called out of order")
        if decision.get("account_id") != self.state.account_id:
            raise GateError("account identity continuity failure")
        hard = decision.get("hard_gates", {})
        if any(v == "FAIL" for v in hard.values()):
            self.state.stage = Stage.REJECT
            self.state.action_class = "REJECT_ADAPTER"
            self._event("QUALIFICATION_REJECT", {"hard_gates": hard})
            return self.state
        if any(v == "UNKNOWN_CRITICAL" for v in hard.values()):
            self.state.stage = Stage.HOLD
            self.state.hold_reason = "CRITICAL_GATE_UNKNOWN"
            return self.state
        action = decision.get("action_class")
        if not action:
            raise GateError("qualification must produce action_class")
        if decision.get("purchase_probability") is not None and not decision.get("calibrated_probability", False):
            raise GateError("uncalibrated purchase probability is forbidden")
        self.state.action_class = action
        self.state.artifact_refs["qualification"] = stable_hash(decision)
        if action == "REJECT_ADAPTER":
            self.state.stage = Stage.REJECT
        elif action in {"HOLD_RESEARCH", "MONITOR_NURTURE"}:
            self.state.stage = Stage.HOLD
            self.state.hold_reason = action
        else:
            self.state.stage = Stage.BUYING_COMMITTEE
        self._event("QUALIFICATION_DECISION", {"action_class": action})
        return self.state

    def buying_committee(self, graph: Dict[str, Any]) -> WorkflowState:
        if self.state.stage != Stage.BUYING_COMMITTEE:
            raise GateError("buying committee called out of order")
        if graph.get("company_intent_attributed_to_person"):
            raise GateError("company intent cannot be attributed to a person")
        if graph.get("title_only_authority_claim"):
            raise GateError("title alone cannot prove ownership/authority")
        if not graph.get("target_contact_id"):
            self.state.stage = Stage.HOLD
            self.state.hold_reason = "NO_JUSTIFIED_CONTACT_ROUTE"
            return self.state
        self.state.artifact_refs["buying_committee"] = stable_hash(graph)
        self._event("BUYING_COMMITTEE_PASS", {"target_contact_id": graph["target_contact_id"]})
        self.state.stage = Stage.PERSUASION
        return self.state

    def persuasion(self, packet: Dict[str, Any]) -> WorkflowState:
        if self.state.stage != Stage.PERSUASION:
            raise GateError("persuasion called out of order")
        if packet.get("borrowed_roi"):
            raise GateError("borrowed ROI is forbidden")
        if packet.get("unsupported_target_pain"):
            raise GateError("unsupported target pain is forbidden")
        if packet.get("renderer_upgraded_epistemic_label"):
            raise GateError("channel renderer cannot upgrade epistemic labels")
        required = ["facts", "hypotheses", "mechanisms", "proofs", "questions", "proposal"]
        if any(k not in packet for k in required):
            raise GateError("incomplete value hypothesis packet")
        self.state.artifact_refs["value_hypothesis"] = stable_hash(packet)
        self._event("PERSUASION_PASS", {})
        self.state.stage = Stage.EXECUTION
        return self.state

    def execute(self, envelope: Dict[str, Any]) -> WorkflowState:
        if self.state.stage != Stage.EXECUTION:
            raise GateError("execution called out of order")
        blockers = []
        if not envelope.get("jurisdiction_resolved", False): blockers.append("JURISDICTION_UNKNOWN")
        if envelope.get("suppressed", False): blockers.append("SUPPRESSED")
        if not envelope.get("approved", False): blockers.append("APPROVAL_MISSING")
        if envelope.get("owner_collision", False): blockers.append("OWNER_COLLISION")
        if blockers:
            self.state.stage = Stage.HOLD
            self.state.hold_reason = ",".join(blockers)
            self._event("EXECUTION_BLOCKED", {"blockers": blockers})
            return self.state
        if envelope.get("provider_result") == "UNCERTAIN":
            self.state.stage = Stage.HOLD
            self.state.hold_reason = "FAILED_UNCERTAIN_RECONCILE"
            self._event("FAILED_UNCERTAIN", {})
            return self.state
        if envelope.get("duplicate_idempotency_key", False):
            self._event("NOOP_DUPLICATE", {})
            self.state.stage = Stage.MEASUREMENT
            return self.state
        self.state.artifact_refs["execution"] = stable_hash(envelope)
        self._event("EXECUTION_SIMULATED", {"channel": envelope.get("channel", "EMAIL")})
        self.state.stage = Stage.MEASUREMENT
        return self.state

    def substantive_reply(self, reply: Dict[str, Any]) -> WorkflowState:
        self._event("SUBSTANTIVE_REPLY", reply)
        self.state.stage = Stage.PAUSED
        self.state.hold_reason = "ACCOUNT_PRODUCT_PAUSED_FOR_REPLY_CLASSIFICATION"
        return self.state

    def measure(self, event_bundle: Dict[str, Any]) -> WorkflowState:
        if self.state.stage != Stage.MEASUREMENT:
            raise GateError("measurement called out of order")
        if event_bundle.get("data_quality") == "FAIL":
            self.state.stage = Stage.HOLD
            self.state.hold_reason = "MEASUREMENT_DATA_QUALITY_FAIL"
            return self.state
        if event_bundle.get("attribution_claimed_as_causal", False):
            raise GateError("CRM attribution cannot be presented as causal lift")
        self.state.artifact_refs["measurement"] = stable_hash(event_bundle)
        self._event("MEASUREMENT_PASS", {})
        self.state.stage = Stage.LEARNING
        return self.state

    def learn(self, update: Dict[str, Any]) -> WorkflowState:
        if self.state.stage != Stage.LEARNING:
            raise GateError("learning called out of order")
        update_class = update.get("update_class")
        grade = update.get("causal_grade", "C0")
        if update_class in {"ROUTING_OR_RANKING_OPTIMIZATION", "PERSUASION_OR_SEQUENCE_OPTIMIZATION"} and grade in {"C0", "C1"}:
            raise GateError("C0/C1 cannot promote performance optimization")
        if update.get("global_policy_change") and not update.get("rollback_target"):
            raise GateError("global policy change requires rollback target")
        if update.get("guardrails") == "FAIL":
            raise GateError("guardrail failure blocks policy promotion")
        self._event("LEARNING_GATE_PASS", {"update_class": update_class, "causal_grade": grade})
        self.state.stage = Stage.ROUTER
        self.state.hold_reason = None
        return self.state

    def _event(self, event_type: str, payload: Dict[str, Any]) -> None:
        self.state.events.append({"type": event_type, "payload": payload})


def demo() -> Dict[str, Any]:
    wf = CertifiedWorkflow(WorkflowState(account_id="acct-demo-001", product_adapter_id="INDUSTRIAL_3DP_BASE"))
    wf.route(["INDUSTRIAL_3DP_BASE"])
    wf.discovery([{"candidate_id":"cand-1","observed_name":"Demo Manufacturing"}], open_world_flag=True)
    wf.evidence({"account_id":"acct-demo-001","decision_readiness":True,"claims":["fixture outsourcing lead time"]})
    wf.qualify({"account_id":"acct-demo-001","hard_gates":{"technical_envelope":"PASS"},"action_class":"PRIORITIZE_OUTBOUND"})
    wf.buying_committee({"target_contact_id":"person-001","roles":["PROBLEM_OWNER"]})
    wf.persuasion({
        "facts":["fixture outsourcing is observed"],
        "hypotheses":["lead time may constrain iteration"],
        "mechanisms":["in-house additive tooling may reduce external queue time"],
        "proofs":["external case evidence"],
        "questions":["does the current lead time delay engineering or production?"],
        "proposal":"review one real fixture workflow",
        "borrowed_roi":False,
    })
    wf.execute({"jurisdiction_resolved":True,"suppressed":False,"approved":True,"owner_collision":False,"provider_result":"SUCCESS","channel":"EMAIL"})
    wf.measure({"data_quality":"PASS","attribution_claimed_as_causal":False,"outcome":"PAIN_CONFIRMED_MEETING"})
    wf.learn({"update_class":"ACCOUNT_FACT_UPDATE","causal_grade":"C0","global_policy_change":False,"guardrails":"PASS"})
    return wf.state.snapshot()


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
