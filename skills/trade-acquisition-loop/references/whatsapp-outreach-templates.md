# WhatsApp 触达模板参考

**硬前提**:没有 consent 或既有业务关系证据(展会交换名片、对方主动留号、邮件里同意换渠道),WhatsApp 草稿永远到不了 `DRAFT_READY`。WhatsApp 在本体系里是**延续渠道**,不是冷启动渠道。

门禁规则:≤60 词且 ≤300 字符;首条不带链接;首条不用 emoji;第一行自报身份;发送窗口收件人当地 09:00–18:00;每 7 天最多 1 条(对方回复前);首触模板需 WhatsApp Business 预审(生产环境)。

## 句段职责(结构)

| 句段 | 职责 |
|---|---|
| 第 1 句 | 自报身份 + 关系锚点(在哪认识/谁介绍/哪封邮件) |
| 第 2 句 | 一句 FACT:对方说过的话或可查证事件 |
| 第 3 句 | 一个问题或一个最小提议(二选一,别都塞) |

## 可粘贴骨架

```text
Hello {{NAME}}, this is {{SENDER_NAME}} from {{COMPANY}} — {{RELATIONSHIP_ANCHOR}}.
{{FACT_SENTENCE_FROM_PRIOR_CONTEXT}}.
{{ONE_QUESTION_OR_SMALLEST_PROPOSAL}}?
```

## 工业 3DP 示例

### 好例子(展会后延续,T1-on-channel)

```text
Hello Mr. Tan, this is Li Wei from Onist 3D — we spoke at the TCT Asia
booth about additive tooling. You mentioned fixture lead times on your
CNC line. Would a short call this week to compare turnaround options
be useful?
```

为什么好:身份+锚点(展位交谈,有证据)、FACT 是对方自己说的话、单一轻量 CTA、44 词、无链接无 emoji。

### 坏例子

```text
Hi! 👋 We are 3D printing factory, best price! Check our catalog
https://example.com and send inquiry! We guarantee fast delivery
and 100% quality! Contact me anytime!!!
```

为什么坏:冷启动无 consent(直接被门禁拒)、emoji、首条带链接、`best price`/`guarantee`/`100% quality` 全部命中禁用模式、无身份锚点、无对方上下文。

## CLO 示例

### 好例子

```text
Hi Ms. Reyes, Ana from Onist here — following up on your note at the
Premiere Vision booth about 3D sampling. Would a 20-minute call next
week on your fit-approval flow work for you?
```

## 跟进触点差异

- **T2-on-channel(≥7 天后)**:只在有新事实时发;一句新信息 + 重述问题。例:`Quick update: the fit-approval checklist we discussed is ready. Still worth 15 minutes on your sampling flow?`
- **T3-on-channel**:收尾,一句话 + 明确停止:`I'll leave it here — if sampling timing comes back up, just message me. Thanks!`
- WhatsApp 上**不做**第 4 触点;序列级收尾统一走 Email T4。

## 约会议(WhatsApp 版)

```text
Two options in your time zone: {{SLOT_1}} or {{SLOT_2}}, 20 minutes,
topic: {{ONE_LINE_AGENDA}}. Which works better?
```

确认与 T-24h 再确认同样走确认包流程;WhatsApp 只承载文本,证据摘要等资产走 Email 发。
