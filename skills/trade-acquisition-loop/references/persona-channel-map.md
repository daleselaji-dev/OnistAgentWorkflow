# 人员定位与渠道映射(Persona Channel Map)

规范源:`contracts/outreach-channel-policy-v1.0.json` 的 `persona_channel_priority`。前提:角色图来自 Buying Committee 阶段,**职位 ≠ 买方角色 ≠ 授权 ≠ 个人意图**。

## 找哪些人(按销售目标选角色,不是按职级扫射)

| 当前销售目标 | 首选角色 | 原因 |
|---|---|---|
| 验证 pain 是否真实 | PROBLEM_OWNER、PRACTITIONER_USER | 离流程最近,回复率最高,不需要授权即可对话 |
| 验证技术可行 | TECHNICAL_EVALUATOR | 决定"能不能用" |
| 推进商务 | ECONOMIC_BUYER(需 champion 或证据支撑才直接触达) | 冷触 economic buyer 需要更强的触发证据 |
| 已有内部响应,扩大共识 | EXECUTIVE_SPONSOR、IMPLEMENTATION_OWNER | 多线程=角色覆盖 |

反模式:一上来群发 CEO;把"账户在招聘"说成"你在找供应商";同一角色连发三个人。

## 渠道选择(角色 × 渠道优先级)

| 角色 | 首选 | 次选 | 说明 |
|---|---|---|---|
| PROBLEM_OWNER | | LinkedIn | 工程/开发负责人习惯邮件处理正事 |
| PRACTITIONER_USER | LinkedIn | Email | 一线从业者社区活跃,peer 语气 |
| TECHNICAL_EVALUATOR | Email | LinkedIn | 需要可转发、可存档的技术内容 |
| ECONOMIC_BUYER | Email | LinkedIn | 正式、简短、直指业务结果假设 |
| EXECUTIVE_SPONSOR | LinkedIn | Email | 高管更看 peer 信号与转介绍 |
| PROCUREMENT_COMMERCIAL_GATE | Email | — | 只走正式渠道 |

WhatsApp 定位:**延续渠道**(展会后、转介绍后、对方同意后),在 SEA/LATAM/MEA 外贸场景常用;冷启动一律禁止(代码强制)。

## 区域适配要点(生产部署前需按辖区法务复核)

| 区域 | 要点 |
|---|---|
| EU/UK | B2B 邮件需辖区级合规解析(GDPR/PECR);语气正式;避开 7–8 月假期季 |
| 北美 | CAN-SPAM 底线(身份+退订);邮件短、直接、结果导向 |
| DACH | 头衔与称谓正式(Herr/Frau + 姓);技术细节接受度高 |
| 东南亚 | WhatsApp 渗透高但仍需 consent;展会(TCT Asia 等)是最佳锚点 |
| 拉美 | WhatsApp 商务常用(consent 后);关系导向,先寒暄一句再谈事 |
| 中东 | 周日–周四工作周;发送窗口按当地工作日历调整 |
| 日韩 | 引荐/展会背书权重极高;冷邮件回复率低,优先 warm path |

时区规则(代码强制):收件人时区必须来自证据台账;未知时区禁止排程。

## 线程计划输出格式

```json
{
  "account_id": "...",
  "product_adapter_id": "...",
  "threads": [
    {"person_id": "...", "role": "PROBLEM_OWNER", "channel_order": ["EMAIL", "LINKEDIN"],
     "timezone": "Europe/Berlin", "consent_whatsapp": false, "connection_accepted": false}
  ],
  "constraints": {"max_parallel": 3, "distinct_roles": true, "pause_scope": "ACCOUNT_PRODUCT"}
}
```
