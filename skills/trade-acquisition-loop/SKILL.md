---
name: trade-acquisition-loop
version: 1.0.0
description: 运行受治理的外贸客户获取闭环(B2B 出海获客)。用于:时机触发式市场调研与目标筛选、渠道与人员定位、开发信/WhatsApp/LinkedIn 触达信撰写、多触点跟进节奏、约会议流程、以及可重复跑的 eval/benchmark 学习回路。构建在 account-to-opportunity skill 之上,复用其证据/资格/价值假设门禁。
---

# Trade Acquisition Loop(外贸获客闭环)

## 定位

本 skill 把 `account-to-opportunity` 的 `PERSUASION -> EXECUTION -> MEASUREMENT` 细化为外贸获客可执行的**渠道草稿 + 跟进/约会议状态机 + 学习回路**。上游(Router / Discovery / Evidence / Qualification / Buying Committee / Value Hypothesis)完全复用 `skills/account-to-opportunity/SKILL.md`,本 skill 不重复也不放松任何上游门禁。

默认行为是调研、起草、dry-run 校验。**本 skill 不是群发工具**:任何真实外发需要授权连接器、辖区/合规解析、抑制名单检查与审批,与主 skill 的生产边界一致。

## 规范合约(machine-readable,代码可执行)

- `contracts/timing-trigger-taxonomy-v1.0.json` — 什么时候找哪些公司(时机触发分类 + 激活评分)
- `contracts/outreach-channel-policy-v1.0.json` — Email / LinkedIn / WhatsApp 渠道适配硬规则
- `contracts/followup-meeting-state-machine-v1.0.json` — 跟进与约会议状态机 + cadence
- 运行时:`workflow/acquisition.py`(渠道门禁、状态机、时机评分、benchmark 循环器)

## 硬性执行契约(在主 skill 十条之上追加)

1. **无日期、无证据的时机触发不得激活外呼**;触发过期只降级为 timing UNKNOWN,不是负面。
2. 触达信必须绑定冻结的 `ValueHypothesisPacket`(`value_packet_ref`)且 FACT 句可回溯到证据 claim id(`fact_claim_ids`)。
3. 禁止承诺型 ROI(中英文)、禁止把账户意图说成个人意图、禁止伪装熟人、禁止虚假紧迫感 —— 由 `forbidden_patterns` 正则在代码门禁里强制执行。
4. WhatsApp 冷启动禁止:没有 consent 或既有业务关系证据的 WhatsApp 草稿永远到不了 `DRAFT_READY`。
5. LinkedIn 只允许人工执行(平台条款),agent 只产草稿;首条消息不带链接、不 pitch。
6. 收件人时区未知则禁止排程;发送窗口按收件人当地时间。
7. 实质性回复立即暂停同一 Account × Product 的全部自动化线程(含并行多线程),人工分类后才能继续。
8. 每序列最多 4 触点、触点间隔 ≥3 天;换渠道需先给首渠道 ≥2 次机会;换人需要不同 buying role 且 90 天内 ≤2 次。
9. 会议无确认包(议程/双方角色/时区/时长/链接/证据摘要/T-24h 再确认)不得进入 `MEETING_CONFIRMED`;会后 24h 内 debrief 必须写回证据台账。
10. 单次成功(C0)永远不能晋升全局话术/序列策略;晋升走 `learning-release-policy-v1.0` 因果门禁。

## Modes

### `research-timing` — 时机触发式市场与公司调研
决定"**现在**值得研究哪些公司"。步骤:
1. 读 `references/timing-trigger-taxonomy.md`,为当前 adapter 选相关触发族。
2. 用触发族的信号源做 Discovery(与主 skill `discover` mode 共享源族与 open-world 语义)。
3. 每个候选公司建触发 claim:`trigger_id + observed_date + evidence_ref`(入证据台账)。
4. 用 `score_timing_triggers` 打分:`OUTBOUND_NOW / DISCOVERY_OUTREACH / MONITOR_NURTURE`。
5. 公司背调完备性按 benchmark 要求:`entity_identity / business_activity_fit / timing_trigger / contactable_role / jurisdiction_zone` 五项 SUPPORTED+source 才算 decision-ready。
产物:带触发分与证据引用的优先级队列;无触发的 fit-only 公司进 watchlist,不冷呼。

### `channel-persona` — 渠道与人员定位
决定"通过什么渠道联系哪些人"。步骤:
1. 复用主 skill `committee` mode 产出的角色图(禁止 title=授权推断)。
2. 按 `persona_channel_priority`(渠道合约内)为每个角色选首选渠道与备选渠道。
3. 检查渠道准入:Email 需辖区可解析;LinkedIn 需可人工执行;WhatsApp 需 consent 证据。
4. 输出 thread plan:每个 account × product 最多 3 个并行线程,角色必须不同。
产物:`{person, role, channel_order, consent_flags, timezone}` 线程计划。

### `draft-outreach` — 触达信撰写
按渠道写信。**先读对应模板 reference,再写,写完必须过 `ChannelDraftGate`**:
- Email:`references/email-outreach-templates.md`
- WhatsApp:`references/whatsapp-outreach-templates.md`
- LinkedIn:`references/linkedin-outreach-templates.md`
规则:每封信 = ValueHypothesisPacket 的渠道压缩渲染;FACT 句必须引用具体可查证事件;HYPOTHESIS 保持条件式("如果…可能…");PROOF 只讲机制可能性;QUESTION 必须能关闭一个实质未知;PROPOSAL 是最小下一步。占位符全部解析后才能交付。

### `follow-up` — 跟进
按 `references/followup-meeting-playbook.md` 的 cadence 执行:
T1(day 0, Email)→ T2(day 3, Email 新角度)→ T3(day 7, LinkedIn 角色转向)→ T4(day 14, Email 收尾信 / 有 consent 时 WhatsApp)。
每个触点必须带**新信息**(新事实/新证据角度/新角色框架),禁止"just bumping"。状态转移全部走 `FollowUpStateMachine`,违规间隔/超量触点会被门禁直接拒绝。

### `meeting-book` — 约会议
标准请求:收件人时区的 2 个具体时段 + 20–25 分钟 + 一句话议程 + 双方参会角色。
异议处理分支、确认包、会前 T-24h 再确认、会后 24h debrief:见 `references/followup-meeting-playbook.md`。
会后三出口:`QUALIFIED_OPPORTUNITY`(交接商机流程)/ `NURTURE`(登记再触发条件)/ `CLOSED_LOST`(挂原因分类)。

### `eval-loop` — 评估与基准
1. 跑 `python -m unittest discover -s tests -v`(合规、状态机、cadence、学习门禁全绿才算 CERTIFIED_DRY_RUN)。
2. 跑 `python workflow/acquisition.py --demo`(集成链路演示)。
3. 用 `AcquisitionLoopRunner` 跑 `examples/trade-acquisition-benchmark.json` 多轮 fixture:同输入必须同哈希(可重复性)。
4. 新一轮真实运行的修正(话术、节奏、渠道顺序)先进 eval dataset;全局晋升必须过 `check_policy_promotion` 因果门禁。

### `resume`
读 `PROJECT.md` → `cache/recovery-packet.md` → 本文件 → 三个合约 → `workflow/acquisition.py`。仓库状态优先于会话记忆。

## Reference loading

- 时机与目标筛选:`references/timing-trigger-taxonomy.md`
- 渠道与人:`references/persona-channel-map.md`
- 写信:对应渠道模板文件(见上)
- 跟进/约会议:`references/followup-meeting-playbook.md`
- 上游阶段:`../account-to-opportunity/SKILL.md` 及其 references

## 认证门禁

`CERTIFIED_DRY_RUN` 条件与主仓库一致:全部 unittest 通过 + demo 闭环。真实外发另需部署级合规审查(辖区、发件域、抑制名单、CRM 权限等,见 `PROJECT.md` production blockers)。
