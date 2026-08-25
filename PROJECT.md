# OnistAgentWorkflow — Project Control

- Status: trade-acquisition loop v1.0 integrated; certified dry-run
- Run mode: engineering/design project with stage gates
- Current stage: trade-acquisition-loop integration
- Current stage gate: PASS
- Last stable architecture: `docs/architecture.md` + `docs/trade-acquisition-loop.md`
- Certified dry-run workflow: `workflow/workflow.json` + `workflow/runtime.py` + `workflow/acquisition.py`
- Reusable skills: `skills/account-to-opportunity/SKILL.md`, `skills/trade-acquisition-loop/SKILL.md`
- Canonical integration version: v1.0

## Purpose

Build an evidence-grounded closed-loop B2B sales-intelligence workflow that discovers candidate companies, verifies account evidence, qualifies product fit/pain/intent/timing, maps buying committees, constructs bounded value hypotheses, governs outreach, measures business outcomes and improves through controlled learning.

## Stable runtime spine

`Router -> Market Universe -> Evidence -> Qualification -> Buying Committee -> Value Hypothesis -> Governed Execution -> Measurement -> Controlled Learning -> Versioned Policy -> loop`

## Certification state

Local deterministic test suite must pass before a revision is called `CERTIFIED_DRY_RUN`. Production outbound remains blocked until deployment-specific readiness gates are resolved.

## Accepted production blockers

1. actual industrial-3DP technical envelope;
2. target jurisdictions / recipient classes / seller legal entity;
3. sender domain/provider and deliverability controls;
4. CRM write permissions and account ownership/collision policy;
5. suppression/privacy operations;
6. exact business metric semantics and sales-cycle horizon;
7. historical calibration data;
8. experiment assignment/contamination infrastructure.

## Trade acquisition loop (v1.0 extension)

`PERSUASION -> EXECUTION -> MEASUREMENT` is refined into a governed trade-acquisition loop: timing-trigger targeting, channel/persona routing, Email/LinkedIn/WhatsApp draft gates, follow-up + meeting state machine, and a repeatable benchmark harness. See `docs/trade-acquisition-loop.md`, `skills/trade-acquisition-loop/SKILL.md`, `workflow/acquisition.py`, and the three contracts `timing-trigger-taxonomy-v1.0.json` / `outreach-channel-policy-v1.0.json` / `followup-meeting-state-machine-v1.0.json`. All existing gates and `CERTIFIED_DRY_RUN` semantics are unchanged.

## Resume entry point

Read in order:
1. `PROJECT.md`
2. `cache/recovery-packet.md`
3. `docs/architecture.md`
4. `docs/trade-acquisition-loop.md`
5. `workflow/WORKFLOW.md`
6. `skills/account-to-opportunity/SKILL.md`
7. `skills/trade-acquisition-loop/SKILL.md`
8. `contracts/cross-stage-handoff-contract-v1.0.json`
9. `contracts/stage-eval-matrix-v1.0.json`
10. `contracts/followup-meeting-state-machine-v1.0.json`

## Next safe action

Select one real product adapter + territory, implement Phase 1 read-only intelligence connectors, and run the trade-acquisition benchmark against real (read-only) trigger data. Do not enable live sending before production-readiness review.
