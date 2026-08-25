# 开发信(Cold Email)模板参考

所有草稿必须通过 `ChannelDraftGate`(`contracts/outreach-channel-policy-v1.0.json`):
首触 ≤120 词、主题 ≤60 字符、≤1 链接、必须披露发件人身份 + 退订方式、禁 ROI 承诺/占位符残留/垃圾开头。

## 句段职责(结构)

| 句段 | 职责 | 绑定 ValueHypothesisPacket |
|---|---|---|
| 主题 | 3–6 词,指向对方自己的上下文(事件/部门/流程),不是你的产品 | FACT |
| 第 1 句 | 具体、可查证的观察:招聘/扩产/展会/发布——必须能回溯到证据 claim | FACT |
| 第 2 句 | 条件式假设:"如果 X 仍是 Y,那么 Z 可能…" | HYPOTHESIS |
| 第 3 句 | 机制 + 外部证明(讲"别人如何做到",显式说明"是否适用取决于…") | MECHANISM + PROOF |
| 第 4 句 | 一个能关闭实质未知的问题 | QUESTION |
| 第 5 句 | 最小下一步(兴趣型 CTA,不是硬约日历) | PROPOSAL |
| 签名 | 真实姓名 + 公司 + 退订方式 | 合规 |

## 可粘贴骨架(占位符交付前必须全部解析)

```text
Subject: {{OBSERVED_TOPIC}} at {{ACCOUNT_SHORT_NAME}}

Hi {{FIRST_NAME}} — {{FACT_SENTENCE_CITING_OBSERVABLE_EVENT}}.

If {{CURRENT_STATE_ASSUMPTION}}, {{CONDITIONAL_CONSEQUENCE}}.

{{PEER_CLASS}} teams have {{MECHANISM_RESULT_AS_POSSIBILITY}};
whether that applies depends on {{ACCOUNT_SPECIFIC_VARIABLE}}.

{{FALSIFIABLE_QUESTION}}?

If useful, {{SMALLEST_NEXT_STEP}}.

{{SENDER_NAME}}, {{SENDER_COMPANY}}
{{OPT_OUT_LINE}}
```

## 工业 3DP 示例

### 好例子(T1)

```text
Subject: Fixture lead time at Nordwerk

Hi Ms. Keller — saw your posting for an additive manufacturing engineer
for the Stuttgart line. If your jigs and fixtures are still outsourced,
iteration may be waiting on external machine-shop queues. Automotive
tooling teams have moved fixture turnaround from weeks to days by
printing in-house; whether that mechanism applies depends on your part
mix and materials. Are fixture lead times currently gating line
changeovers? If useful, I can walk through one of your live fixture
workflows in 20 minutes.

Li Wei, Onist 3D — reply "no thanks" and I won't write again.
```

为什么好:FACT 指向具体招聘帖(可回溯);假设是条件式;外部证明只讲机制并声明适用性未知;问题可证伪;CTA 是最小步;98 词。

### 坏例子(每一处都会被门禁拒绝或应被 review 打回)

```text
Subject: Best 3D printing solution for your business!!

Dear Sir, we are a leading manufacturer of 3D printers with best price
and 100% quality. I know you are looking for a printing supplier. We
guarantee we can save you 30% on tooling costs. Act now for a limited
time discount! Please see attached catalog.
```

为什么坏:`Dear Sir`(SPAM_OPENER)、`leading manufacturer`/`best price`/`100% quality`(HYPE_SUPERLATIVE)、`I know you are looking`(把账户意图当个人意图)、`guarantee ... save you 30%`(ROI 承诺双重违规)、`Act now / limited time`(虚假紧迫感)、无事实、无问题、无最小步。

## CLO 示例

### 好例子(T1)

```text
Subject: Sampling rounds at Blue Atelier

Hi Maya — noticed the 3D fashion designer (CLO) opening on your careers
page. If sample development is still physical-first, each fit iteration
may be adding courier weeks before market dates. Brands moving to
3D-first development have cut physical rounds per style; whether that
transfers depends on your fit process and factories. Are sample
iterations the bottleneck ahead of your next market week? Happy to map
one style's sampling flow together in 20 minutes.

Ana Ruiz, Onist Digital Fashion — tell me to stop and I will.
```

### 坏例子

```text
Subject: CLO software partnership opportunity

Hello dear, our 3D software is used by all top brands. You will get
faster samples and lower cost guaranteed. When can we schedule a demo
of all our modules this week?
```

为什么坏:无事实锚点、`all top brands` 不可查证、`You will get ... guaranteed` 承诺型 ROI、CTA 直接硬索时间且范围过大("all our modules")。

## 跟进触点差异(T2 / T3 / T4)

**T2(day 3,同渠道,≤80 词)— 新角度,不是催**
```text
Subject: Re: {{T1_SUBJECT}}

One more data point since my last note: {{SECOND_FACT_OR_PROOF_ANGLE}}.
The reason I ask about {{TOPIC}} is {{LIKELY_OBJECTION_PREEMPTED}}.
{{RESTATED_QUESTION_DIFFERENT_ANGLE}}?
```
要求:必须携带 T1 没有的新事实/新证明角度;预答一个最可能的异议;问题换角度重问。禁止 "just following up / bumping this"。

**T3(day 7,默认换 LinkedIn;若留 Email 则换角色框架)**
```text
{{ROLE_PIVOT_OBSERVATION}} — perhaps this sits with someone else on
your team. If {{TOPIC}} isn't yours, could you point me to whoever owns
{{PROCESS}}? And if it is yours: {{ONE_SENTENCE_QUESTION}}?
```
要求:显式提供"转介绍"降级出口(opt-down);换一个 buying-role 视角重述价值假设。

**T4(day 14,收尾信)**
```text
Subject: closing the loop

{{FIRST_NAME}} — I'll stop here. If {{TRIGGER_CONDITION}} comes back on
your roadmap, the note below has the one-page summary we prepared for
{{ACCOUNT_SHORT_NAME}}. No reply needed.
```
要求:专业收尾、留一份价值资产(一页纸摘要)、明确不再打扰、状态机进 `NURTURE` 并登记再触发条件。

## 约会议请求(Email 版标准话术)

```text
Would 20 minutes work to review {{ONE_LINE_AGENDA}}?
I can do {{SLOT_1_LOCAL_TZ}} or {{SLOT_2_LOCAL_TZ}} ({{RECIPIENT_TZ}}).
From our side {{OUR_ROLE}} joins; useful if {{THEIR_ROLE}} joins too.
```

异议处理分支见 `followup-meeting-playbook.md`。
