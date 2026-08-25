# Recovery Packet

- Current stage: trade-acquisition-loop integration (v1.0)
- Current stage gate: PASS (54 unittest methods green; both demos close their loops)
- Last stable artifacts: docs/architecture.md + docs/trade-acquisition-loop.md
- Runtime: workflow/workflow.json + workflow/runtime.py + workflow/acquisition.py
- Skills: skills/account-to-opportunity/SKILL.md + skills/trade-acquisition-loop/SKILL.md
- New contracts: timing-trigger-taxonomy-v1.0.json / outreach-channel-policy-v1.0.json / followup-meeting-state-machine-v1.0.json
- Benchmark: examples/trade-acquisition-benchmark.json (discovery recall/diversity, dossier completeness, 14 draft fixtures, 3 scripted loop rounds; deterministic result hash)
- Canonical version: v1.0
- Open production blockers: unchanged (jurisdiction/recipient policy; sender readiness; CRM write scope; suppression/privacy; technical envelope; metric semantics; calibration data; experiment topology) + WhatsApp Business template pre-approval + LinkedIn human-execution constraint
- Stale rule: revalidate product/provider/legal/source assumptions before production implementation; deployment-specific legal/compliance review is always required for live outreach
- Next safe action: pick one adapter + territory, run research-timing mode against real read-only trigger sources, human-review channel drafts produced by draft-outreach mode, and replay the acquisition benchmark
- Resume prompt: Continue OnistAgentWorkflow from the trade-acquisition-loop stable state. Read PROJECT.md and cache/recovery-packet.md first. Use the account-to-opportunity skill for upstream stages and the trade-acquisition-loop skill for timing research, channel drafts, follow-up, meetings, and eval. Keep live external actions blocked until production-readiness gates are explicitly resolved.
