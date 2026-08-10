# Internal Engineering Certification — v1.0

Status target: **CERTIFIED_DRY_RUN**

This is an **internal engineering verification**, **not** a legal, regulatory, security, privacy, deliverability, or third-party certification.

A repository revision is `CERTIFIED_DRY_RUN` only when all of the following pass:

1. workflow state-machine tests;
2. stage hard-gate tests;
3. canonical contract parse/integrity tests;
4. cross-stage handoff coverage;
5. reply/suppression/idempotency safety semantics;
6. learning-release guardrails;
7. reference 3DP/CLO dry-run examples remain parseable;
8. GitHub Actions `certify` job is green.

## Production certification is separate

Live sending is **not certified** by this repository. Before live execution, a deployment-specific review must resolve jurisdiction, recipient class, seller entity, sender infrastructure, opt-out/suppression, privacy, CRM write permissions, ownership/collision rules, product technical envelope, metrics, sales-cycle horizon and experiment topology.

## Command

```bash
python -m unittest discover -s tests -v
```

## Release gate

- Tests green: `CERTIFIED_DRY_RUN`
- Any hard-gate test red: `NOT_CERTIFIED`
- Live integrations without production-readiness review: `DRY_RUN_ONLY`

## v1.0 validation snapshot

- 21 unittest methods: PASS locally
- 87 Chapter C–G deterministic fixture cases: PASS locally
- Chapter A/B fixture sets: parse/integrity PASS locally
- Full deterministic demo closes the loop back to `ROUTER`: PASS locally
- Live-send production gate: BLOCKED pending deployment-specific readiness
