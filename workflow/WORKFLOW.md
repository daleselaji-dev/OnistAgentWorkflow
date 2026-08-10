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

## Certification

Run:

```bash
python -m unittest discover -s tests -v
```

A release is `CERTIFIED_DRY_RUN` only when all tests pass. Live execution is a separate deployment gate.
