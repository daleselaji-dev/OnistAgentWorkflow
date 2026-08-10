# Recovery Packet

- Current stage: handoff-close
- Current stage gate: PASS
- Last stable artifact: docs/architecture.md
- Runtime: workflow/workflow.json + workflow/runtime.py
- Skill: skills/account-to-opportunity/SKILL.md
- Canonical version: v1.0
- Open production blockers: product technical envelope; jurisdiction/recipient policy; sender readiness; CRM write scope; suppression/privacy process; ownership collision; metric semantics; calibration data; experiment topology
- Stale rule: revalidate product/provider/legal/source assumptions before production implementation; deployment-specific legal/compliance review is always required for live outreach
- Next safe action: implement a read-only pilot for one adapter and one territory, benchmark discovery recall and evidence quality, then human-review qualification/contact/value outputs
- Resume prompt: Continue OnistAgentWorkflow from the handoff-close stable state. Read PROJECT.md and cache/recovery-packet.md first. Use the account-to-opportunity skill. Keep live external actions blocked until production-readiness gates are explicitly resolved.
