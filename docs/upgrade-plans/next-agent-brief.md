# Next-Agent Brief — 外贸智能硬件升级计划执行简报

- 隶属计划：`UPGRADE_FOREIGN_TRADE_SMART_HARDWARE_V1`
- 主计划：`docs/upgrade-plans/foreign-trade-smart-hardware-v1.md`（先读它，再读本文件）
- 形态决策：`docs/upgrade-plans/decision-matrix.md`
- 当前应执行阶段：**Phase 1**（Phase 0 已随本计划 PR 完成）

## 启动提示（Resume Prompt，直接复制给执行 Agent）

> Continue OnistAgentWorkflow from the certified v1.0 dry-run state. Read `PROJECT.md`, `cache/recovery-packet.md`, then `docs/upgrade-plans/foreign-trade-smart-hardware-v1.md` and `docs/upgrade-plans/next-agent-brief.md`. Execute Phase 1 of the upgrade plan: create the `skills/foreign-trade-lead-gen` skill, the `SMART_HARDWARE_IOT_EXPORT` adapter, v1.1 additive contracts, the smart-hardware dry-run example, and the new contract tests — without modifying any v1.0 contract, workflow, or existing test assertion. All work stays dry-run; live outreach remains BLOCKED. Acceptance: `python3 -m unittest discover -s tests -v` fully green including the new v1.0-freeze regression test.

## 全局约束（任何阶段不得违反）

1. **v1.0 冻结**：不修改任何 `*-v1.0.json` 合约、`workflow/workflow.json`（Phase 2 前）、`runtime.py`（Phase 2 前）及现有测试断言。只允许新增。
2. **Live outreach 保持 BLOCKED**：不实现、不调用任何真实外发通道；一切执行走 dry-run 语义。
3. **fail-closed**：关键未知 → HOLD，不允许分数或措辞绕过硬门槛。
4. **provenance**：所有决策承载 claim 与产品自述字段必须带来源标签；`CLAIMED_UNVERIFIED` 不得进入 FACT 位或对外表述。
5. **认证语义**：完成后 `python3 -m unittest discover -s tests -v` 必须全绿，否则按 `CERTIFICATION.md` 属 `NOT_CERTIFIED`，需先修复。

## Phase 1 Checklist（逐文件任务清单）

| # | 任务 | 产出路径 | 验收 |
|---|---|---|---|
| 1 | 新建外贸 Skill 主文件：modes 至少含 `product-intake`、`advantage-playbook`、`discover`、`qualify`、`persuade`、`prepare-action`（dry-run）、`resume`；通用阶段纪律**引用** `skills/account-to-opportunity/SKILL.md`，不复制 | `skills/foreign-trade-lead-gen/SKILL.md` | frontmatter 含 name/version/description；无与 v1.0 skill 冲突的规则 |
| 2 | Smart-hardware adapter 参考文档：照主计划 §4 落全（jobs、hard gates 表含 FAIL 判据、信号族、角色映射、负控制） | `skills/foreign-trade-lead-gen/references/smart-hardware-adapter.md` | 六个 hard gate 均有可判定 FAIL 判据 |
| 3 | 外贸 source families 参考（主计划 §4.3 展开，含每族的授权/合规注意） | `skills/foreign-trade-lead-gen/references/source-families.md` | 每个源族标注允许的访问方式 |
| 4 | 合规门槛参考（认证/频段/数据合规细目，按目标市场分组） | `skills/foreign-trade-lead-gen/references/compliance-gates.md` | 与 adapter hard gates 一一对应 |
| 5 | 报价阶梯参考（spec sheet → 样品 → 报价 → 试单；每台阶的证据前提） | `skills/foreign-trade-lead-gen/references/offer-ladder.md` | 每台阶标注允许进入的最低证据水平 |
| 6 | 本体 v1.1：在 v1.0 全量内容基础上新增 `SMART_HARDWARE_IOT_EXPORT` | `contracts/canonical-ontology-v1.1.json` | v1.0 文件字节不变；v1.1 为超集 |
| 7 | Product-intake 合约：SellerProductProfilePacket + AdvantagePlaybookPacket 字段、provenance 枚举（`DOC_VERIFIED`/`MEASURED`/`CLAIMED_UNVERIFIED`）、FACT 位准入规则 | `contracts/product-intake-contract-v0.1.json` | JSON 可解析；含 forbidden 规则字段 |
| 8 | 发现政策 v1.1：新增外贸源族；保持 open-world 语义声明 | `contracts/universe-discovery-policy-v1.1.json` | v1.0 文件不变 |
| 9 | 回复路由 v1.1：新增外贸 reply taxonomy（INQUIRY / SAMPLE_REQUEST / QUOTE_REQUEST / PRICE_NEGOTIATION / FACTORY_AUDIT_REQUEST / OPT_OUT 等），实质回复→PAUSED 语义不变 | `contracts/reply-routing-policy-v1.1.json` | v1.0 文件不变 |
| 10 | Smart-hardware 端到端 dry-run 示例（结构对齐 `examples/industrial-3dp-e2e-dry-run.json`，execution.live_send=false） | `examples/smart-hardware-e2e-dry-run.json` | 被 `test_contracts.py` 的 glob 自动解析通过 |
| 11 | 新合约测试：① 新 JSON 全部可解析；② v1.1 本体含新 adapter 且为 v1.0 超集；③ **v1.0 冻结回归**（对全部 `*-v1.0.json` + `workflow/workflow.json` 记录并断言 sha256）；④ 新 example 存在 | `tests/test_foreign_trade_contracts.py` | `python3 -m unittest discover -s tests -v` 全绿 |
| 12 | `CERTIFICATION.md` 验证快照追加 smart-hardware fixture 一行（不改判定标准，production gate 保持 BLOCKED） | `CERTIFICATION.md` | 现有 `test_no_fake_external_certification_language` 仍通过 |
| 13 | 更新 `PROJECT.md` / `cache/recovery-packet.md`：stage 推进为 Phase 1 完成、next safe action 指向 Phase 2 | 两文件 | 语义与认证状态一致 |

完成顺序建议：6→7→8→9（合约先行）→ 1→5（skill 引用合约）→ 10 → 11 → 12→13。全程小步 commit。

## Phase 2 Checklist（Product Intake 状态机化）

1. `workflow/workflow.json` 升 v1.1：stages 头部插入 `{"id":"PRODUCT_INTAKE","kind":"agentic_bounded","next":["ROUTER","HOLD"]}`；`global_invariants` 增加 `unverified_seller_claim_cannot_enter_fact_position`。
2. `runtime.py`：`Stage` 增加 `PRODUCT_INTAKE`；新增 `product_intake(profile)` 方法——`CLAIMED_UNVERIFIED` 字段被标记进 FACT 用途 → `GateError`；缺关键档案字段 → HOLD（`PRODUCT_PROFILE_INCOMPLETE`）。
3. `contracts/cross-stage-handoff-contract-v1.1.json`：在 v1.0 handoffs 基础上新增 `PRODUCT_INTAKE→ROUTER`（required: `seller_product_profile_ref`,`advantage_playbook_ref`,`provenance_summary`）。
4. `contracts/stage-eval-matrix-v1.1.json`：v1.0 全量 + `PRODUCT_INTAKE` 条目（quality: 字段 provenance 完备率、claim 判定一致率；hard gates: 未验证声明不得入 FACT）。
5. 新增 unittest：demo 从 `PRODUCT_INTAKE` 起步闭环回 `ROUTER`；`CLAIMED_UNVERIFIED` 入 FACT 位抛 `GateError`。旧测试断言零修改。

## Phase 3 Checklist（读只读 pilot，摘要）

1. 选定 1 个 territory（欧盟或北美）+ 1–2 个只读源（海关数据、展会名录），核实服务条款允许程序化访问；不可得则降级为人工 CSV 导入。
2. 建 known-positive benchmark（≥20 个已知真实买家账户）。
3. 跑 discovery→evidence→qualification，全部输出人审；修正记录进 eval dataset。
4. 产出召回/证据质量报告；**零 live 外发**。

## 验证步骤（文档审阅 + 测试）

**文档审阅 checklist（Phase 0 交付验收用）**：

- [ ] 主计划十个章节齐全（scope / 形态决策 / spine 映射 / adapter / 五能力落位 / 路线图 / 文件清单 / 认证影响 / 叙事建议 / resume prompt）
- [ ] 形态决策有明确结论且含反方论证（decision-matrix §4）
- [ ] 所有新增能力均为 additive，未要求修改任何 v1.0 认证产物
- [ ] Live outreach 在所有阶段描述中保持 BLOCKED
- [ ] Wide early / Strict late、FACT→…→PROPOSAL、fail-closed、provenance 四条设计思想均有具体落点（非口号）
- [ ] 每个 Phase 有目标/交付物/验收标准/风险/任务清单

**测试**：

```bash
python3 -m unittest discover -s tests -v   # 当前基线 16 个用例应全绿
python3 workflow/runtime.py --demo          # 应闭环回 ROUTER
```
