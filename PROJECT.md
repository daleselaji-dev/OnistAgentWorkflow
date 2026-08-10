# OnistAgentWorkflow — Project Control

- Status: handoff-close complete; GitHub release ready
- Run mode: engineering/design project with stage gates
- Current stage: handoff-close
- Current stage gate: PASS
- Last stable architecture: `docs/architecture.md`
- Certified dry-run workflow: `workflow/workflow.json` + `workflow/runtime.py`
- Reusable skill: `skills/account-to-opportunity/SKILL.md`
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

## Resume entry point

Read in order:
1. `PROJECT.md`
2. `cache/recovery-packet.md`
3. `docs/architecture.md`
4. `workflow/WORKFLOW.md`
5. `skills/account-to-opportunity/SKILL.md`
6. `contracts/cross-stage-handoff-contract-v1.0.json`
7. `contracts/stage-eval-matrix-v1.0.json`

## Next safe action

Select one real product adapter + territory and implement Phase 1 read-only intelligence connectors. Do not enable live sending before production-readiness review.
