# 跟进与约会议 Playbook

规范源:`contracts/followup-meeting-state-machine-v1.0.json`(状态、转移、门禁全部由 `FollowUpStateMachine` 代码强制)。本文件是人读的执行手册。

## 状态机总览

```text
DRAFT_READY --send_approved--> SENT --opened--> OPENED
SENT/OPENED --no_reply_window(3d)--> NO_REPLY
NO_REPLY --followup_due--> FOLLOWUP_1 --followup_due--> FOLLOWUP_2
        --followup_due--> FOLLOWUP_3 --sequence_exhausted--> NURTURE

任意活跃态 --reply_substantive--> HUMAN_TAKEOVER(整个 Account x Product 自动化暂停)
任意活跃态 --opt_out--> UNSUBSCRIBED(抑制名单,终态)
任意活跃态 --bounce_hard/policy_block--> HOLD(回上游修数据/修策略)

HUMAN_TAKEOVER --meeting_interest--> MEETING_PROPOSED --slot_accepted--> MEETING_BOOKED
  --确认包齐全--> MEETING_CONFIRMED --meeting_held--> MEETING_HELD
  --debrief 齐全--> QUALIFIED_OPPORTUNITY / NURTURE / CLOSED_LOST
HUMAN_TAKEOVER --not_now--> NURTURE | --rejection--> CLOSED_LOST | --wrong_person--> HOLD(回 Buying Committee)
```

## 跟进节奏(cadence)

| 触点 | 日 | 默认渠道 | 模板 | 内容差异要求 |
|---|---|---|---|---|
| T1 | 0 | | T1_OPENER | FACT→HYPOTHESIS→MECHANISM/PROOF→QUESTION→PROPOSAL 全链 |
| T2 | +3 | Email | T2_NEW_ANGLE | 必须带 T1 没有的新事实/新证明角度;预答一个异议;更短(≤80 词) |
| T3 | +7 | LinkedIn | T3_ROLE_PIVOT | 换角色框架 + 显式转介绍出口("不归您管的话,指个方向?") |
| T4 | +14 | Email(有 consent 可 WhatsApp) | T4_BREAKUP | 专业收尾 + 留一页纸价值资产 + 明确不再打扰 |

硬规则(代码强制):触点间隔 ≥3 天;每序列 ≤4 触点;换新渠道前旧渠道 ≥2 触点;WhatsApp 需 consent;LinkedIn 需连接已接受;时区未知不排程。

## 换渠道 / 换人 / 并行多线程

- **换渠道**:同渠道 2 次无回复后允许切换;回到用过的渠道随时允许(频率限制内)。
- **换人**:仅在 (a) 序列耗尽无互动(NURTURE 后)或 (b) 对方明确转介绍(HOLD 回 Buying Committee)时;新联系人必须是**不同 buying role**;每 account × product 90 天内 ≤2 次换人。
- **并行多线程**:每 account × product 最多 3 个并行线程,角色必须互不相同(multi-threading = 角色覆盖,不是联系更多人);**任一线程收到实质性回复,所有线程一起暂停**。

## 实质性回复后的人工接管(HUMAN_TAKEOVER)

1. 自动化立即暂停(Account × Product 范围,含并行线程)。
2. 人工在 1 个工作日内分类:`meeting_interest / not_now / rejection / wrong_person / OOO-auto`(OOO/自动回复按 reply-routing-policy 只暂停该人线程,可 `resume_automation`)。
3. 分类结果作为 claim 写回证据台账(回复内容是最高价值的账户证据)。
4. 只有人工分类事件能离开 HUMAN_TAKEOVER。

## 约会议流程

### 标准请求话术
两个具体时段(收件人时区)+ 时长 + 一句话议程 + 双方角色:
```text
Would 20 minutes work to review {{ONE_LINE_AGENDA}}?
I can do {{SLOT_1}} or {{SLOT_2}} ({{RECIPIENT_TZ}}).
From our side {{OUR_ROLE}} joins; useful if {{THEIR_ROLE}} joins too.
```
无回应:48–72h 后**一次**提醒(换一个时段选项),再无回应 → `NURTURE`,不纠缠。

### 异议处理分支

| 异议 | 应对 | 状态去向 |
|---|---|---|
| "先发资料" | 发一页纸价值假设(非全套 deck),同时提议"看完 15 分钟对一下是否相关" | MEETING_PROPOSED 保持 |
| "现在不合适" | 问出再触发条件("下次打样周期/预算周期什么时候?"),登记触发后进 NURTURE | NURTURE |
| "已有供应商" | 不贬低对手;定位为基准对比/第二货源;问一个量化问题("现在的交期/单件成本是多少?") | HUMAN_TAKEOVER 继续 |
| "太贵/没预算" | 不降价;问"什么样的结果能让这笔预算成立",转价值量化会议 | MEETING_PROPOSED 或 NURTURE |
| "找错人了" | 致谢 + 请求转介绍;新线程走 Buying Committee 重新路由 | HOLD → 换人流程 |
| 明确拒绝 | 致谢收尾,挂 `closed_lost_reason` 分类 | CLOSED_LOST |

### 会前确认包(缺一不可,代码强制)

`agenda_one_liner / attendee_roles_both_sides / recipient_timezone_confirmed / duration_minutes / dial_in_or_location / evidence_summary_ref / t24h_reconfirm_scheduled`

T-24h 再确认信:
```text
Looking forward to tomorrow {{TIME_LOCAL_TZ}}. Agenda: {{ONE_LINE_AGENDA}}.
{{OUR_SIDE}} will join from our side. Link: {{DIAL_IN}}. Still good?
```
No-show:不指责,当天轻量重约;重约累计 ≤2 次,超限 → NURTURE。

### 会后 24 小时内(debrief,代码强制)

1. `notes_to_evidence_ledger`:会议中确认的事实全部变成带来源的 claim(来源=会议记录)。
2. `reply_classification`:PAIN_CONFIRMED / TIMING_NOT_NOW / NO_FIT / REFERRAL。
3. `next_action` 三选一:
   - `QUALIFIED_OPPORTUNITY`:买方确认 pain + 存在下一步(技术评估/样件/试点),交接商机流程;
   - `NURTURE`:登记具体再触发条件(预算周期、产线时点、展会),到期由时机触发重新进 QUALIFICATION;
   - `CLOSED_LOST`:挂原因分类(NO_TECHNICAL_FIT / INCUMBENT_LOCKED / NO_BUDGET_HORIZON / EXPLICIT_NOT_INTERESTED / COMPLIANCE_BLOCKED)。

## 测量与学习

每个状态转移都是可测事件(`measurement_events`)。漏斗:touch_sent → open → reply → meeting_booked → meeting_held → qualified。
- 账户层事实(某公司交期 3 周)→ C0 即可更新账户记忆。
- 话术/节奏的全局改动 → 必须过 `check_policy_promotion`:CANARY ≥C3、BROAD ≥C3+复现,offline eval + guardrails + rollback 齐全。单次会议成功永远不能改全局模板。
