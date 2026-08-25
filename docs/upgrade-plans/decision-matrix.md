# 形态背调与评估矩阵 — Workflow vs Skill vs Agent

- 隶属计划：`UPGRADE_FOREIGN_TRADE_SMART_HARDWARE_V1`（主文件：`foreign-trade-smart-hardware-v1.md`）
- 评估对象：外贸获客流程（产品信息提取 → 优势打法总结 → 寻找客户 → 说服客户 → 后续销售）应以何种形态构建。
- 评估基线：本仓库 v1.0 已认证设计原则——*Durable deterministic workflow backbone + bounded agentic reasoning nodes + governed data/evidence services + human/policy gates*。

## 1. 三种候选形态定义

| 形态 | 定义（在本仓库语境下） | 现有对应物 |
|---|---|---|
| **Workflow** | 确定性编排 + 状态机：状态转移、门控、lineage、idempotency、HOLD/REJECT/PAUSED 分支由代码强制 | `workflow/workflow.json` + `runtime.py` |
| **Skill** | 可复用 Agent Skill（SKILL.md + references）：方法论、阶段纪律、硬失败清单的知识封装，供任意 Agent 运行时加载 | `skills/account-to-opportunity/SKILL.md` |
| **Agent** | 自主/半自主代理：给定目标后自行规划-执行-迭代，含工具调用与外部动作决策权 | 无（v1.0 有意避免，仅以 bounded agentic nodes 存在） |

## 2. 逐维评估

评分：`++` 强优势 / `+` 优势 / `0` 中性 / `-` 劣势 / `--` 强劣势。

| 维度 | Workflow | Skill | Agent | 说明 |
|---|:---:|:---:|:---:|---|
| 状态与断点续跑（durable state） | ++ | - | - | 只有 deterministic runtime 能保证 checkpoint/resume/lineage |
| 安全不变量强制（suppression/jurisdiction/idempotency） | ++ | - | -- | Skill 是约定，Agent 是意愿；只有代码是保证 |
| 开放世界任务（发现/研究/写作） | -- | + | ++ | fuzzy 任务硬编码进 workflow 既脆又贵 |
| 方法论复用与传播 | 0 | ++ | - | SKILL.md 可被任何兼容 Agent 环境加载；Agent 逻辑难移植 |
| 可审计性 / 可回溯性 | ++ | + | -- | 外贸合规场景（认证声明、跨境营销法）必须可回溯 |
| 可测试性 / 可认证性 | ++ | + | -- | Skill 的纪律可被合约测试间接约束；自主 Agent 行为不可穷举 |
| 迭代成本（改打法、换品类） | - | ++ | 0 | 换品类 = 换 adapter 文档 + 政策文件，Skill 最便宜 |
| 幻觉风险暴露面 | ++ | + | -- | Agent 直接对外 = borrowed ROI / 认证谎报的最大暴露面 |
| 求职作品集信号 | + | ++ | - | 「受治理的混合架构」是稀缺信号；「auto-SDR」已是红海且有负面联想 |
| 公司落地阻力（合规/管理层批准） | ++ | + | -- | 批准一份政策文件容易，批准一个自主外发 Agent 很难 |
| 与 v1.0 spine 契合度 | ++（就是它） | ++（平行于既有 skill） | --（被 v1.0 明确否决："deliberately avoids a single autonomous super-agent"） | |

## 3. 逐能力归属分析

| 能力 | 任务性质 | 最佳归属 |
|---|---|---|
| 产品信息提取 | 语言密集、文档解析、需 provenance 纪律 | **Skill mode（`product-intake`）+ 合约约束**；Phase 2 升格为状态机 stage 获得 gate 测试保护 |
| 优势打法总结 | 假设生成、需 FACT/HYPOTHESIS 分离 | **Skill mode（`advantage-playbook`）**，打法晋升走 Workflow 的 learning-release gate |
| 寻找客户 | 开放世界高召回搜索 + 确定性硬门槛 | **既有 spine**：DISCOVERY（agentic node）→ EVIDENCE → QUALIFICATION（deterministic） |
| 说服客户 | 有界推理 + epistemic 合约 | **既有 spine**：BUYING_COMMITTEE + PERSUASION（bounded agentic under contract） |
| 后续销售 | 副作用治理、序列状态、回复中断 | **既有 spine**：EXECUTION + PAUSED + MEASUREMENT + LEARNING（deterministic） |

结论从表中直接可读：五个能力没有一个的最佳归属是「自主 Agent」；两个新能力归 Skill（受合约约束），三个既有能力归已认证 spine。

## 4. 反方论证（为什么不是纯 Agent —— steelman 后仍否决）

**支持纯 Agent 的最强论据**：外贸获客高度依赖临场判断（议价、跟单节奏、文化差异），自主 Agent 端到端处理可最大化响应速度，且市场上 auto-SDR 产品热度高，演示效果好。

**否决理由**：

1. **合规不可逆**：跨境外发触碰 GDPR、CAN-SPAM、各国反垃圾邮件法；一次违规外发不可撤回。v1.0 的 fail-closed 原则要求未知即阻断，自主 Agent 的默认行为模式与此相反（未知即尝试）。
2. **认证声明的法律重量**：智能硬件外贸沟通中的 CE/FCC/UN38.3 声明是准法律陈述。LLM 幻觉一次「我们有 CE 认证」，代价不是一封尴尬邮件而是合同违约。这正是 `CLAIMED_UNVERIFIED` 不得外泄这条设计（主计划 §5.1）存在的原因——该设计只能由 deterministic gate 保证。
3. **学习污染**：自主 Agent 会从单次成交「学到」全局策略，恰是 v1.0 `C0/C1 不得晋升 performance policy` 硬门槛防止的事故模式。
4. **不可演示的失败**：作品集/公司评审场景中，Workflow+Skill 的每个决策可展示 lineage；自主 Agent 只能展示结果，无法展示「为什么可信」。

**保留的 Agent 成分**：spine 内的 bounded agentic nodes（DISCOVERY 搜索、EVIDENCE 综合、COMMITTEE 角色假设、PERSUASION 包构建、以及新增的 intake/playbook 两个 mode）——即「Agent 在节点内思考，Workflow 在节点间掌权」。

## 5. 最终决策

> **混合架构**：v1.0 deterministic workflow spine 保持骨干地位（零修改），外贸获客五能力以**新 Skill（`foreign-trade-lead-gen`）+ 新 adapter（`SMART_HARDWARE_IOT_EXPORT`）+ v1.1 增量合约**的形式加入；其中「产品信息提取」「优势打法总结」为 Skill 新 modes（Phase 2 升格为状态机 stage），「找客户 / 说服客户 / 后续销售」直接复用既有阶段。自主 Agent 形态被明确否决，agentic 推理仅存在于受合约约束的节点内。

决策落地路径与验收标准见主计划 §6 路线图。
