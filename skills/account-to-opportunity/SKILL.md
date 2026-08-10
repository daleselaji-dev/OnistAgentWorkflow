---
name: account-to-opportunity
version: 1.0.0
description: Design, review, or run a governed B2B Account-to-Opportunity sales-intelligence workflow. Use for product/ICP routing, candidate-company discovery, company research and provenance, fit/pain/intent/timing qualification, buying-committee mapping, value-hypothesis design, human-reviewed outreach preparation, funnel measurement, causal evaluation, and controlled policy learning.
---

# Account-to-Opportunity

## Purpose

Turn market/account information into traceable sales decisions:

```text
Product / Problem
-> Market Universe
-> Evidence Ledger
-> Qualification
-> Buying Committee
-> Value Hypothesis
-> Governed Action Preparation
-> Measurement
-> Controlled Learning
-> loop
```

This skill is **not** a bulk lead spammer, scraping bot, or free-running autonomous SDR. Default behavior is research, analysis, recommendation, drafting, and dry-run validation. Any live external action requires an explicitly authorized connector, applicable policy/compliance checks, suppression checks, and the required human or policy approval.

## Execution contract

1. Identify the current stage and canonical account/product scope.
2. Read only the minimum references needed for that stage.
3. Complete the stage's decision job before advancing.
4. Fail closed on critical unknowns: HOLD, repair, re-search, human review, or reject the product adapter.
5. Never convert a discovered candidate directly into a qualified account.
6. Never let later stages strengthen an upstream claim without new evidence.
7. Never infer personal buying intent from account-level intent.
8. Never transplant an external case-study ROI into a target account.
9. Do not use unauthorized scraping, browser automation, or bulk unsolicited messaging.
10. Global performance policy may change only through the learning-release gate; single-case success and CRM attribution are insufficient.

## Modes

- `design`: create/revise architecture and contracts.
- `discover`: high-recall candidate-company discovery using allowed sources.
- `research`: build a versioned account evidence ledger.
- `qualify`: choose the next commercial action from frozen evidence.
- `committee`: map buying roles and contact-route hypotheses.
- `persuade`: build a ValueHypothesisPacket before any channel copy.
- `prepare-action`: produce human-reviewable drafts/tasks and run policy checks.
- `execute-dry-run`: simulate execution/state transitions with no live side effect.
- `measure`: normalize funnel/reply/guardrail events.
- `learn`: update account truth/evals or propose a versioned policy change under the release gate.
- `review-repair`: find hard failures and emit the smallest repair contract.
- `resume`: read PROJECT.md, cache/recovery-packet.md, then the last stable artifact.

## A — Product / Problem Router

Translate each product into jobs-to-be-done, pains, prerequisites, observable signals, buyer-role hypotheses and negative controls.

- Multi-label routing is allowed.
- Industry labels and generic “3D” keywords are weak proxies.
- Product capability changes trigger adapter revalidation.

## A2 — Market Universe / Candidate Discovery

Goal: maximize relevant account recall without pretending an open-world market is complete.

Use multiple allowed source families and expand by job, role, pain proxy, technology, trigger, geography/language and competitor/alternative.

Hard failures:
- candidate presented as qualified;
- one source family treated as the whole market;
- blocked source replaced with unauthorized scraping;
- brand/subsidiary forced into one account without identity evidence;
- search absence treated as account non-existence;
- fake completeness claims.

## B — Evidence Ledger / Research

Resolve entity identity and create atomic decision-bearing claims.

Keep distinct:
- source vs evidence;
- publisher vs original source;
- event time vs retrieval time;
- UNKNOWN vs NOT_FOUND_AFTER_COVERAGE vs NEGATIVE_VERIFIED;
- account intent vs person intent.

Research pattern:
`discovery -> targeted discovery -> verification -> contradiction hunt -> freshness/negative check -> coverage/stop`.

Hard failures: wrong entity merge, unsupported decision claim, citation that does not entail the claim, not-found treated as negative, stale evidence silently presented as current.

## C — Qualification

Decide the next action, not a vanity lead score.

Keep separate:
- Fit
- Pain
- Intent
- Timing
- Capacity / Strength
- Buyer Expected Value
- Seller Expected Value
- Evidence Confidence

Apply hard gates first. Evidence confidence limits what action is allowed; it is not a score bonus.

Actions:
`REJECT_ADAPTER`, `ROUTE_ALTERNATE_PRODUCT`, `HOLD_RESEARCH`, `MONITOR_NURTURE`, `DISCOVERY_OUTREACH`, `PRIORITIZE_OUTBOUND`, `FAST_TRACK`.

Do not state a calibrated purchase probability without real historical calibration.

## D — Buying Committee

Determine who can advance the next sales goal.

Do not conflate job title, organizational scope, buying role, authority, employment status or personal intent.

Relevant roles may include problem owner, practitioner, champion candidate, technical evaluator, implementation owner, economic buyer, executive sponsor, procurement, IT/security/data gate, legal/compliance, influencer and blocker.

Multi-threading means distinct-role coverage, not contacting many people.

## E — Value Hypothesis

Freeze the reasoning chain before any message rendering:

```text
FACT -> HYPOTHESIS -> MECHANISM -> PROOF -> QUESTION -> PROPOSAL
```

- Facts require target-account evidence.
- Hypotheses stay visibly conditional and falsifiable.
- External customer results are proof of possibility/mechanism, not guaranteed target ROI.
- Questions should close a material unknown or change the next decision.
- Proposal = smallest appropriate next step.
- Channel drafts may compress language but may not upgrade epistemic status.

## F — Governed Action Preparation / Execution

Before any live side effect, require applicable checks for:
- jurisdiction / recipient / channel policy;
- authorized connector/channel;
- sender readiness;
- suppression / opt-out;
- account ownership collision;
- human/policy approval;
- idempotency;
- current sequence state.

Rules:
- unknown jurisdiction blocks live execution;
- provider-uncertain result is reconciled, never blindly retried;
- a substantive human reply pauses the same Account × Product motion before classification;
- unauthorized browser/social automation is blocked;
- bulk or high-volume unsolicited outreach is outside the default skill behavior.

## G — Measurement / Controlled Learning

Separate:
1. account memory;
2. cohort hypothesis;
3. eval dataset;
4. production policy.

Attribution is not incrementality.

Causal grades:
- C0 observation
- C1 attributed association
- C2 quasi-experimental
- C3 valid randomized experiment
- C4 replicated/transportable evidence

Single-case outcomes and C0/C1 may update account truth or hypotheses, but cannot broadly promote performance optimization.

## Cross-stage handoff

Durable artifacts preserve at minimum:
- `account_id`
- `product_adapter_id`
- `artifact_id`
- `artifact_version`
- `content_hash`
- `created_at`

Later artifacts must link contacts, actions, traces, events, experiments and policy versions to exact upstream artifacts. Chapter-local PASS is not end-to-end PASS if the joins break.

## Reference adapters

### Industrial 3D printing
Jobs: prototyping, jigs/fixtures, rapid tooling, high-mix/low-volume, replacement parts. Production qualification also needs the seller's actual technical envelope: process, material, build volume, throughput, accuracy, environmental/regulatory constraints, price band and service geography.

### CLO family
- `CLO_FASHION_DPC`: apparel product development / sampling / technical design.
- `MD_CG_CLOTH`: game/VFX/animation/CG garment assets.
- `CLOFAB_FABRIC_DIGITIZATION`: textile/fabric digitization and digital-material workflows.
- `CLOSET_3D_WORKSPACE`: 3D asset/version/review/collaboration/product-lifecycle workflows.

## Review / repair gate

For a failed artifact emit:

```text
Repair Contract
- Failing stage:
- Responsible component:
- Weak / unsafe behavior:
- Required change:
- Re-test / re-review condition:
- State/cache update:
- Next stage allowed: yes / no
```

## Certification gate

A repository release is `CERTIFIED_DRY_RUN` only after:

```bash
python -m unittest discover -s tests -v
```

passes. This is internal engineering verification, not legal/regulatory/third-party certification. Live deployment requires a separate readiness review.

## Reference loading

- Full design/review: `references/architecture-summary.md`, `references/stage-gates.md`, `references/product-adapters.md`.
- Discovery: stage gates + product adapters + universe contracts.
- Research/qualification: stage gates + evidence/qualification contracts.
- Action preparation: stage gates + execution/suppression contracts.
- Learning: stage gates + causal grades + learning-release policy.

For durable projects, repo state is canonical over chat memory.
