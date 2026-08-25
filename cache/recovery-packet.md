# Recovery Packet

- Current stage: handoff-close
- Current stage gate: PASS
- Last stable artifact: docs/architecture.md
- Runtime: workflow/workflow.json + workflow/runtime.py
- Skill: skills/account-to-opportunity/SKILL.md
- Canonical version: v1.0
- Open production blockers: product technical envelope; jurisdiction/recipient policy; sender readiness; CRM write scope; suppression/privacy process; ownership collision; metric semantics; calibration data; experiment topology
- Stale rule: revalidate product/provider/legal/source assumptions before production implementation; deployment-specific legal/compliance review is always required for live outreach
- Approved upgrade plan: docs/upgrade-plans/foreign-trade-smart-hardware-v1.md (Phase 0 complete; Phase 1 pending)
- Next safe action: execute Phase 1 of the foreign-trade smart-hardware upgrade plan per docs/upgrade-plans/next-agent-brief.md — additive-only skill/adapter/contracts/example/tests; do not modify any v1.0 certified artifact; keep everything dry-run
- Resume prompt: Continue OnistAgentWorkflow from the certified v1.0 dry-run state. Read PROJECT.md, cache/recovery-packet.md, then docs/upgrade-plans/foreign-trade-smart-hardware-v1.md and docs/upgrade-plans/next-agent-brief.md. Execute Phase 1 additively. Keep live external actions blocked until production-readiness gates are explicitly resolved.
