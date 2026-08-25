# Certified Workflow Specification

## Workflow ID

`ONIST_ACCOUNT_TO_OPPORTUNITY_V1`

## Inputs

Required:
- product adapter(s);
- territory / market boundary;
- source access policy;
- discovery budget;
- seller / CRM context when execution is enabled.

Production execution additionally requires a resolved jurisdiction policy and approved sender/CRM configuration.

## Stages

1. **ROUTER** — map products to jobs/problems/signals; multi-label output.
2. **DISCOVERY** — high-recall candidate-account discovery; never qualify here.
3. **EVIDENCE** — entity resolution + atomic claim/evidence ledger.
4. **QUALIFICATION** — hard gates, then Fit/Pain/Intent/Timing/Capacity/Value; output action class.
5. **BUYING_COMMITTEE** — role graph and next-contact route.
6. **PERSUASION** — freeze `FACT/HYPOTHESIS/MECHANISM/PROOF/QUESTION/PROPOSAL` packet.
7. **EXECUTION** — policy/approval/suppression/idempotency gate + durable side effect.
8. **MEASUREMENT** — normalize funnel/guardrail events; preserve assignment and lineage.
9. **LEARNING** — account updates immediately; global policy only through versioned release gate.

## Branches

- `REJECT` — hard product/technical/compliance mismatch.
- `HOLD` — critical unknown or policy blocker; return to the responsible upstream stage.
- `MONITOR_NURTURE` — fit exists but timing/intent window is weak.
- `DISCOVERY_OUTREACH` — contact to validate pain/ownership, not to over-pitch.
- `PRIORITIZE_OUTBOUND` — evidence supports targeted outbound.
- `FAST_TRACK` — active vendor dialogue/procurement/decision window.

## Invariants

1. One account/product lineage uses stable canonical IDs.
2. Every decision-bearing claim is traceable to evidence.
3. Hard gates cannot be overridden by a score.
4. Account-level intent cannot be attributed to an individual without person-level evidence.
5. External proof never becomes target-account guaranteed ROI.
6. No external action can bypass suppression/jurisdiction/approval/idempotency.
7. Provider-uncertain side effects are reconciled before retry.
8. Substantive replies pause account × product automation before classification.
9. CRM attribution does not equal causal incrementality.
10. C0/C1 evidence cannot broadly promote performance optimization.

## Extension: trade-acquisition outreach sub-machine (v1.0)

`TRADE_ACQUISITION_LOOP_V1` refines `PERSUASION -> EXECUTION -> MEASUREMENT` without changing the top-level spine or any existing gate:

1. **Channel drafts** — the frozen ValueHypothesisPacket renders into Email / LinkedIn / WhatsApp drafts; `workflow/acquisition.py::ChannelDraftGate` enforces `contracts/outreach-channel-policy-v1.0.json` (length, tone register, link count, consent, timezone window, forbidden ROI/spam patterns, unresolved placeholders, evidence traceability). A violating draft never reaches `DRAFT_READY`.
2. **Follow-up / meeting states** — each governed send enters `contracts/followup-meeting-state-machine-v1.0.json`: `DRAFT_READY -> SENT -> OPENED/NO_REPLY -> FOLLOWUP_1..3 -> NURTURE`, with global interrupts `reply_substantive -> HUMAN_TAKEOVER` (pauses the whole account x product motion), `opt_out -> UNSUBSCRIBED`, `bounce/policy -> HOLD`, and the meeting path `MEETING_PROPOSED -> MEETING_BOOKED -> MEETING_CONFIRMED -> MEETING_HELD -> QUALIFIED_OPPORTUNITY / NURTURE / CLOSED_LOST`. Cadence (>=3-day intervals, <=4 touches, channel/person-switch caps, confirmation pack, debrief) is code-enforced.
3. **Timing triggers** — `contracts/timing-trigger-taxonomy-v1.0.json` + `score_timing_triggers` order the outbound queue; an undated or unevidenced trigger cannot activate outreach, and trigger scores can never override a hard qualification gate.
4. **Benchmark loop** — `AcquisitionLoopRunner` replays `examples/trade-acquisition-benchmark.json` rounds deterministically (identical input => identical result hash) and `check_policy_promotion` blocks single-case global policy promotion.

Run the integrated dry-run demo:

```bash
python workflow/acquisition.py --demo
```

## Certification

Run:

```bash
python -m unittest discover -s tests -v
```

A release is `CERTIFIED_DRY_RUN` only when all tests pass. Live execution is a separate deployment gate.
