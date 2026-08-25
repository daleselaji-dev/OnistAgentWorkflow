# 系统升级计划 — 外贸获客流程（Phase 1 适配域：外贸智能硬件 / IoT）

- 计划 ID：`UPGRADE_FOREIGN_TRADE_SMART_HARDWARE_V1`
- 状态：`PLAN_APPROVED_PENDING_EXECUTION`（本文件即计划本体；实现由下一个执行 Agent 完成）
- 基线：v1.0 `CERTIFIED_DRY_RUN`（`docs/architecture.md` + `workflow/workflow.json` + `workflow/runtime.py`，16 unittest 全绿）
- 辅助文件（同目录）：
  - `decision-matrix.md` — Workflow / Skill / Agent 三形态背调评估全矩阵
  - `next-agent-brief.md` — 下一个执行 Agent 的启动简报与任务清单
- 升级原则：**不推翻已认证架构，只做增量扩展（additive versioning）**。现有 v1.0 合约、状态机、测试保持不动；新能力以 v1.1 合约与新 Skill 的形式加入。

---

## 1. 目标与非目标（Scope）

### 1.1 目标

建立完整的「外贸获客流程」闭环，覆盖五个业务能力：

```text
产品信息提取 → 优势打法总结 → 寻找客户 → 说服客户 → 后续销售
```

并把它们落到已认证的 v1.0 runtime spine 上：

```text
Router -> Market Universe -> Evidence -> Qualification -> Buying Committee
-> Value Hypothesis -> Governed Execution -> Measurement -> Controlled Learning -> loop
```

Phase 1 适配域：**外贸智能硬件（IoT / 智能硬件出口）**，作为继 Industrial 3DP、CLO 家族之后的第三个参考域。

### 1.2 非目标（明确不做）

1. **不实现 live outreach**。所有外发动作默认 `BLOCKED`，直至 `PROJECT.md` 中 8 项 production blockers 的外贸特化版本被逐项解决并通过部署级评审。
2. **不重写 v1.0 状态机**。`workflow/workflow.json` 与 `runtime.py` 的 v1.0 语义在 Phase 0/1 内不修改；Phase 2 才引入版本化的 v1.1 状态机扩展（见 §6）。
3. **不做自主 SDR super-agent**。见 §2 形态决策。
4. **不承诺校准概率、不借用外部 ROI**。v1.0 全部 epistemic 硬门槛继续适用。
5. **不采购/绑定具体数据供应商**（海关数据、B2B 平台等）。Phase 1 仅定义 source family 与接口合约，供应商选型属 Phase 3 读只读 pilot 的决策。

---

## 2. 形态决策结论（背调评估摘要）

> 完整利弊矩阵、逐维打分与反方论证见同目录 `decision-matrix.md`。

### 2.1 结论

**推荐混合架构（Hybrid）：保持 v1.0 deterministic workflow spine 为骨干，新增一个可复用 Skill 作为 Phase 1 主交付形态，agentic 能力继续以 bounded reasoning nodes 嵌入 spine，不引入 free-running Agent。**

一句话：**Workflow 管状态与安全，Skill 管方法论与复用，Agent 只在受限节点内思考，永远不独立扣扳机。**

### 2.2 理由

| 形态 | 判定 | 核心理由 |
|---|---|---|
| 纯 Workflow | 不足 | 能保证治理，但「产品信息提取 / 优势打法总结 / 说服话术」是语言密集、开放世界的 fuzzy 任务，硬编码进确定性节点会既僵硬又不可维护。 |
| 纯 Skill | 不足 | Skill 无法自行保证 idempotency、suppression、lineage、learning-release 等运行时不变量——这些必须由 deterministic runtime 强制。 |
| 纯 Agent（自主/半自主） | 否决 | 外贸获客涉及跨境合规（GDPR、CAN-SPAM、各国反垃圾邮件法）、认证声明（CE/FCC）与价格承诺，自主 Agent 的不可审计性与幻觉风险直接命中 v1.0 的多条硬门槛（borrowed ROI、epistemic 升级、未知 jurisdiction 外发）。求职展示上，"又一个 auto-SDR" 也是反向信号。 |
| **混合（推荐）** | **采纳** | 与既有认证原则逐字吻合：*Durable deterministic workflow backbone + bounded agentic reasoning nodes + governed data/evidence services + human/policy gates*。新域只需：① 新 product adapter；② 新 Skill（方法论封装）；③ v1.1 增量合约。零破坏、可认证、可展示。 |

### 2.3 与 v1.0 spine 的契合度

- v1.0 spine 的 9 个 stage 覆盖外贸获客五能力中的后三个（找客户、说服客户、后续销售），**无需新增 stage 即可承载**（映射见 §3）。
- 前两个能力（产品信息提取、优势打法总结）是 Router 的**上游输入生产**问题：v1.0 假设 product adapter 已存在，外贸场景需要「从原始产品资料生成 adapter 实例」的能力。Phase 1 把它建模为 Router 阶段的两个新输入产物（不改状态机）；Phase 2 再决定是否版本化为显式 `PRODUCT_INTAKE` stage（见 §5.1、§6）。

### 2.4 对求职作品集与公司落地的价值

- 作品集：展示的是「架构判断力」而非「会调 API」——同一 spine 三个域（3DP / CLO / 智能硬件外贸）复用，证明抽象层选得对；形态决策矩阵本身就是可讲述的设计故事（详见 §9）。
- 公司落地：Skill 形态让销售/市场同事能在任何支持 Agent Skill 的环境中调用同一套方法论；deterministic spine 让合规与管理层敢于批准，因为每个外发动作可回溯到证据版本与审批记录。

---

## 3. 与现有 spine 的映射

外贸智能硬件域在 v1.0 九阶段上的逐段映射（`保持` = 语义不变仅加载新 adapter；`扩展` = 需要 v1.1 增量产物/政策）：

| v1.0 Stage | 外贸域职责 | 变更类型 |
|---|---|---|
| **Product Router** | 消费新产物 `SellerProductProfilePacket` + `AdvantagePlaybookPacket`（§5.1/§5.2），把智能硬件产品多标签路由到 jobs-to-be-done（ODM 采购 / 渠道分销 / 方案集成 / 自有品牌扩品类 / 垂直方案）。 | 扩展（新输入产物 + 新 adapter） |
| **Market Universe** | 高召回候选买家发现。新增外贸 source families：海关进口记录、展会名录（CES/IFA/广交会/Global Sources）、认证公开库（FCC ID / CE 数据库）、B2B 平台目录、零售/电商上架信号、竞品分销商名单、招聘信号、众筹平台。保持 `OPEN_WORLD_NOT_COMPLETE` 语义。 | 扩展（`universe-discovery-policy-v1.1` 增补 source families） |
| **Evidence** | 实体解析（进口商/分销商/品牌商母子公司）+ 原子 claim。外贸特有：海关记录的 event time 与 retrieval time 分离；`UNKNOWN` ≠ `NOT_FOUND_AFTER_COVERAGE` ≠ `NEGATIVE_VERIFIED` 继续适用（例如"查不到该公司进口记录"不等于"该公司不进口"）。 | 保持 |
| **Qualification** | 硬门槛前置：目标市场认证匹配（CE/FCC/UKCA/RoHS/UN38.3/RED 等）、频段协议合规、MOQ×产能匹配、物流/关税可行性、数据合规（带云/App 产品的 GDPR）。硬门槛不可被分数补偿。输出仍是 action class。 | 扩展（adapter 专属 hard gates，复用 v1.0 action classes） |
| **Buying Committee** | 外贸买方角色图谱：采购总监、品类经理、硬件 PM、认证/合规工程师、供应链/QA、渠道 owner。头衔 ≠ 采购角色 ≠ 权限 ≠ 个人意向，继续适用。 | 保持（roles 复用 v1.0 ontology，参考文档给外贸命名映射） |
| **Value Hypothesis** | `FACT -> HYPOTHESIS -> MECHANISM -> PROOF -> QUESTION -> PROPOSAL` 不变。外贸特化：PROPOSAL 使用「报价阶梯」（spec sheet → 样品 → 报价 → 试单），FACT 只能来自 SellerProductProfile 中 provenance 为 VERIFIED 的字段（§5.2）。 | 扩展（offer-ladder 参考 + FACT 来源约束） |
| **Governed Execution** | 全部 v1.0 门槛（jurisdiction/suppression/approval/idempotency/owner collision）继续强制；外贸加严：未解析目标国 = 未知 jurisdiction = 阻断。**Live outreach 默认保持 BLOCKED。** | 保持（政策参数外贸化，机制不变） |
| **Measurement** | 外贸漏斗事件：询盘 → 样品请求 → 报价 → 试单 → 返单；guardrail：投诉/退订/黑名单率。attribution ≠ causality 不变。 | 扩展（事件 taxonomy 增补） |
| **Learning** | 账户事实即时更新；打法（AdvantagePlaybook 的 HYPOTHESIS 段）晋升为全局策略必须走 learning-release gate，C0/C1 不得晋升 performance policy。 | 保持 |
| **HOLD / REJECT / PAUSED 分支** | 全部保持。外贸新增典型 HOLD 原因示例：`CERTIFICATION_GAP_UNKNOWN`、`TARGET_MARKET_REGULATORY_UNRESOLVED`。 | 保持（hold reason 词表增补） |

---

## 4. 新增产品适配器设计：`SMART_HARDWARE_IOT_EXPORT`

新 adapter 加入 `canonical-ontology-v1.1.json` 的 `product_adapter_ids`（v1.0 文件不动）。

### 4.1 Jobs-to-be-done（多标签路由目标）

1. `ODM_WHITE_LABEL_SOURCING` — 进口商/品牌商寻找白牌或 ODM 智能硬件供应。
2. `CHANNEL_DISTRIBUTION` — 区域分销商为渠道补充智能硬件品类。
3. `SOLUTION_INTEGRATION` — 系统集成商需要可集成的硬件模块（追踪器、传感器、网关）。
4. `BRAND_CATEGORY_EXPANSION` — 已有品牌向智能品类扩张（如传统家居品牌上智能款）。
5. `VERTICAL_IOT_DEPLOYMENT` — 垂直行业（物流、冷链、农业、养老）的 IoT 设备采购。

### 4.2 硬门槛（非补偿性，进入 Qualification hard_gates）

| Gate ID | 内容 | FAIL 判据示例 |
|---|---|---|
| `CERT_TARGET_MARKET` | 目标市场强制认证（CE/FCC/UKCA/RoHS/REACH；含电池则 UN38.3；无线则 RED/SRRC/IC） | 产品无 CE 而目标买家只售欧盟 |
| `RF_BAND_PROTOCOL` | 频段/协议区域合规（BLE/Wi-Fi/LoRa/NB-IoT/Cat-M 的区域频段与运营商支持） | NB-IoT 频段与目标国运营商不匹配 |
| `MOQ_CAPACITY_MATCH` | 买方期望订量落在卖方 MOQ 与产能区间 | 买方试单量低于工厂 MOQ 且无小单柔性 |
| `LOGISTICS_TARIFF_FEASIBLE` | HS code 归类、关税、认证清关、DDP 能力可行 | 目标国对该 HS code 有禁限或关税使报价失去竞争力 |
| `DATA_COMPLIANCE` | 带云服务/App 的产品满足目标市场数据法规（GDPR 等） | 云端在境外且无合规方案，买家为欧盟渠道 |
| `IP_CLEAN` | 目标市场无已知专利/外观侵权风险 | 已知专利纠纷覆盖目标市场 |

判定值沿用 v1.0：`PASS` / `FAIL` / `UNKNOWN_CRITICAL`（触发 HOLD，不允许分数绕过）。

### 4.3 信号族（Observable signal families，供 Universe/Evidence 使用）

海关进口记录（品类 HS code + 供应商切换信号）、展会参展/观展名录、FCC ID 与 CE 公开数据库（竞品买家反查）、B2B 平台询盘行为、零售/电商上架与评论、渠道商官网品类页、招聘信号（硬件采购/品类经理岗）、众筹平台（品牌方寻供应链信号）、行业媒体与获投新闻。

### 4.4 买方角色映射（复用 v1.0 buying_roles）

| v1.0 role | 外贸典型头衔（假设，需人证） |
|---|---|
| `ECONOMIC_BUYER` | 采购总监 / Head of Sourcing / Owner（中小进口商） |
| `PROBLEM_OWNER` | 品类经理 / Product Line Manager |
| `TECHNICAL_EVALUATOR` | 硬件 PM / 认证合规工程师 |
| `IT_SECURITY_DATA_GATE` | 数据合规 / 云安全负责人（带 App 产品） |
| `PROCUREMENT_COMMERCIAL_GATE` | 采购 / 供应链 / QA（验厂主导方） |
| `CHAMPION_CANDIDATE` | 渠道 owner / 区域销售负责人 |

### 4.5 负控制（Negative controls）

- 「公司名带 smart/IoT」不构成买家信号（弱代理）。
- 目标公司自有工厂且同品类自产 → 大概率 `REJECT_ADAPTER` 或 `ROUTE_ALTERNATE_PRODUCT`（模块供应）。
- 纯软件/平台公司无硬件渠道 → 弱 fit，需证据支持才能进入 outreach 类 action。

---

## 5. 五个业务能力 → 阶段与产物落位

### 5.1 产品信息提取 → `SellerProductProfilePacket`（Router 输入产物 #1）

- **落位**：Phase 1 为 Router 阶段的前置输入产物，由新 Skill 的 `product-intake` mode 生成；**不修改状态机**。Phase 2 评估是否版本化为显式 `PRODUCT_INTAKE` stage（v1.1 状态机）。
- **输入**：产品规格书、认证证书、产线/产能资料、报价表、已有客户案例、工厂口头陈述。
- **产物字段（合约 `product-intake-contract-v0.1.json` 定义）**：规格参数、认证清单（含证书编号与有效期）、MOQ/产能/交期、价格带、知识产权状态、供应链关键依赖、已验证差异点。
- **关键设计（fail-closed + provenance）**：每个字段必须携带 provenance 标签：`DOC_VERIFIED`（有文件）/ `MEASURED`（实测）/ `CLAIMED_UNVERIFIED`（仅口头）。`CLAIMED_UNVERIFIED` 字段**不得**进入后续 AdvantagePlaybook 的 FACT 位，也不得出现在任何对外表述中——这是把 v1.0「evidence provenance」原则向卖方自身信息的对称延伸：**对自己产品的声明与对客户的判断使用同一套证据纪律**。

### 5.2 优势打法总结 → `AdvantagePlaybookPacket`（Router 输入产物 #2）

- **落位**：Skill 的 `advantage-playbook` mode，消费 SellerProductProfilePacket，输出打法包。
- **结构（复用 FACT→HYPOTHESIS 纪律）**：
  - `advantages[]`：每条差异化优势 = FACT（回链 profile 中 `DOC_VERIFIED`/`MEASURED` 字段）+ 相对基准（对比谁、在哪个 segment）；禁止无锚定的「全球领先」「性价比之王」。
  - `plays[]`：每条打法 = segment × region × 进攻假设，显式标注 `HYPOTHESIS`，附可证伪条件与验证信号；打法在获得 C2+ 证据前不得被表述为「已验证策略」。
  - `negative_scope`：明确不打的市场/客群及原因（认证缺失、MOQ 不匹配等）→ 直接为 Qualification hard gates 提供输入。
- **治理**：打法晋升为全局默认策略必须经 learning-release gate（§3 Learning 行）。

### 5.3 寻找客户 → 复用 DISCOVERY + EVIDENCE + QUALIFICATION

- Universe：`universe-discovery-policy-v1.1` 增补 §4.3 信号族为允许 source families；Wide early——多源族并行扩召回，保持开放世界不完备语义。
- Evidence：外贸实体解析重点（进口商/品牌/分销商母子关系；海关记录归属）；claim 原子化 + 双时间戳。
- Qualification：Strict late——§4.2 六个硬门槛前置，然后才做 Fit/Pain/Intent/Timing 分维评估，输出 v1.0 七个 action class 之一。

### 5.4 说服客户 → 复用 BUYING_COMMITTEE + PERSUASION

- Committee：§4.4 角色映射；多线程 = 角色覆盖而非人数。
- Persuasion：ValueHypothesisPacket 结构不变；外贸特化约束：
  - FACT 双源：目标账户证据（对方的 pain/context）+ SellerProductProfile 已验证字段（我方能力），两侧都不许越级；
  - PROOF：已有客户案例只能证明机制可行性，不得移植为目标客户 ROI 承诺；
  - PROPOSAL：使用 offer-ladder（spec sheet → 样品 → 报价 → 试单），默认选择当前证据水平允许的最小台阶。

### 5.5 后续销售 → 复用 EXECUTION + PAUSED + MEASUREMENT + LEARNING

- Execution：sequence state 管理跟进节奏；实质性回复（询价、样品请求、砍价、验厂要求）触发 `PAUSED`，先分类再行动——`reply-routing-policy-v1.1` 增补外贸回复 taxonomy。
- Measurement：外贸漏斗 `INQUIRY → SAMPLE_REQUEST → QUOTE → TRIAL_ORDER → REPEAT_ORDER` + guardrail 事件（投诉/退订/黑名单）。
- Learning：账户级事实即时更新；序列/话术优化必须 C2+ 才可全局晋升。

---

## 6. 分阶段执行路线图

### Phase 0 — 升级计划认证（本 PR，已完成）

- **目标**：形态决策定案 + 完整升级计划入库 + 状态文件指向新计划。
- **交付物**：本文件、`decision-matrix.md`、`next-agent-brief.md`、`PROJECT.md`/`cache/recovery-packet.md` 轻量更新。
- **验收标准**：现有 16 unittest 保持全绿；计划通过人审（checklist 见 `next-agent-brief.md` §验证）。
- **风险**：无代码风险；主要风险是计划粒度不足——已通过 per-phase 任务清单缓解。

### Phase 1 — 外贸 Skill + Smart-hardware adapter（dry-run only）

- **目标**：五能力在 dry-run 语义下端到端可走通，v1.0 认证不受破坏。
- **交付物**：
  1. `skills/foreign-trade-lead-gen/SKILL.md`（新 Skill：modes 含 `product-intake`、`advantage-playbook`，其余阶段委托/引用 `account-to-opportunity` skill）；
  2. `skills/foreign-trade-lead-gen/references/`：`smart-hardware-adapter.md`、`source-families.md`、`compliance-gates.md`、`offer-ladder.md`；
  3. `contracts/canonical-ontology-v1.1.json`（新增 `SMART_HARDWARE_IOT_EXPORT`；v1.0 文件不改）；
  4. `contracts/product-intake-contract-v0.1.json`（SellerProductProfile + AdvantagePlaybook 字段与 provenance 规则）；
  5. `contracts/universe-discovery-policy-v1.1.json`、`contracts/reply-routing-policy-v1.1.json`（外贸源族与回复 taxonomy）；
  6. `examples/smart-hardware-e2e-dry-run.json`（对齐既有两个 example 的结构）；
  7. `tests/test_foreign_trade_contracts.py`（新合约 parse/完整性 + example 存在性 + v1.0 合约未被修改的回归断言）。
- **验收标准**：`python3 -m unittest discover -s tests -v` 全绿（老 16 + 新用例）；新 example 可被 `test_contracts.py` 的 glob 解析；`git diff` 显示 v1.0 合约与 runtime 零改动。
- **风险与缓解**：① adapter 硬门槛主观化 → 每个 gate 必须写出可判定的 FAIL 判据（§4.2 表为模板）；② Skill 与既有 skill 语义漂移 → foreign-trade skill 中所有通用阶段规则用引用而非复制。
- **下一步 Agent 可直接执行的任务清单**：见 `next-agent-brief.md` §Phase 1 checklist（逐文件、逐验收项）。

### Phase 2 — Product Intake 阶段正式化（workflow v1.1）

- **目标**：把 `product-intake`/`advantage-playbook` 从 Skill mode 升格为状态机显式阶段，获得与其他阶段同级的 gate 测试保护。
- **交付物**：`workflow/workflow.json` v1.1（新增 `PRODUCT_INTAKE` stage，`next: ["ROUTER","HOLD"]`）；`runtime.py` 增加 `product_intake()` 方法与硬门槛（`CLAIMED_UNVERIFIED` 字段进入 FACT 位 → `GateError`）；`cross-stage-handoff-contract-v1.1.json` 增加 `PRODUCT_INTAKE→ROUTER` handoff；对应 unittest。
- **验收标准**：demo 从 `PRODUCT_INTAKE` 起步仍闭环回 `ROUTER`；全部旧测试语义不变（只允许新增，不允许改断言）。
- **风险**：状态机版本化策略——采用「同文件版本号升级 + 测试锁定旧不变量」而非并存两份状态机，避免分叉。
- **任务清单**：`next-agent-brief.md` §Phase 2 checklist。

### Phase 3 — 读只读连接器 pilot（单 territory）

- **目标**：接入 1–2 个只读数据源（候选：海关数据、展会名录），在一个 territory（建议欧盟或北美二选一）跑真实 discovery + evidence + qualification，人审全部输出。
- **交付物**：连接器接口合约、known-positive benchmark 集、召回/证据质量报告、人审修正记录（进入 eval dataset）。
- **验收标准**：known-positive recall 达到基准线（由 benchmark 定义）；qualification 输出的人审否决率有记录并回流 eval；**零 live 外发**。
- **风险**：数据供应商条款限制自动化访问 → 选型时把「允许程序化访问」列为硬性采购条件；源不可得时回退人工导入 CSV 的降级路径。
- **任务清单**：`next-agent-brief.md` §Phase 3 checklist。

### Phase 4 — 生产就绪评审与受控外发（gated）

- **目标**：逐项解决 8 个 production blockers 的外贸特化版本（目标国反垃圾邮件法、发件域、CRM 写权限、退订/隐私流程、指标语义、实验拓扑等），通过部署级评审后启用一对一、人审批准的外发。
- **验收标准**：`CERTIFICATION.md` production gate 从 `BLOCKED` 更新为逐项 `RESOLVED` 的评审记录；首批外发全部走 approval + suppression + idempotency 路径且可回溯。
- **风险**：合规评审属外部依赖，不由 Agent 单方面判定——**此阶段必须有人类负责人签字**。

---

## 7. 文件/目录变更清单（计划）

### Phase 0（本 PR 实际新增/修改）

```text
新增  docs/upgrade-plans/foreign-trade-smart-hardware-v1.md   ← 本文件（主计划）
新增  docs/upgrade-plans/decision-matrix.md                    ← 形态评估矩阵
新增  docs/upgrade-plans/next-agent-brief.md                   ← 执行 Agent 启动简报
修改  PROJECT.md                                               ← 指向新计划 + next safe action
修改  cache/recovery-packet.md                                 ← 同上（不改认证状态语义）
```

### Phase 1（计划新增，本 PR 不实现）

```text
skills/foreign-trade-lead-gen/SKILL.md
skills/foreign-trade-lead-gen/references/smart-hardware-adapter.md
skills/foreign-trade-lead-gen/references/source-families.md
skills/foreign-trade-lead-gen/references/compliance-gates.md
skills/foreign-trade-lead-gen/references/offer-ladder.md
contracts/canonical-ontology-v1.1.json
contracts/product-intake-contract-v0.1.json
contracts/universe-discovery-policy-v1.1.json
contracts/reply-routing-policy-v1.1.json
examples/smart-hardware-e2e-dry-run.json
tests/test_foreign_trade_contracts.py
```

### Phase 2（计划修改，版本化）

```text
workflow/workflow.json            → v1.1（新增 PRODUCT_INTAKE stage）
workflow/runtime.py               → 新增 product_intake() 与对应 GateError
contracts/cross-stage-handoff-contract-v1.1.json
tests/test_workflow.py            → 仅新增用例，不改旧断言
```

---

## 8. 合约 / 测试 / 认证影响

1. **v1.0 合约冻结**：`*-v1.0.json` 全部不修改；`tests/test_contracts.py` 现有断言（含 handoff 全 spine 覆盖、stage-eval 阶段集合相等断言）继续原样通过。注意：`test_stage_eval_has_all_runtime_stages` 使用**集合相等**断言，因此 Phase 2 若为 `PRODUCT_INTAKE` 增加 stage-eval 条目，须发布 `stage-eval-matrix-v1.1.json` 并新增对应测试，而不是改 v1.0 文件。
2. **增量测试策略**：Phase 1 的 `test_foreign_trade_contracts.py` 应包含一条「v1.0 冻结回归」断言（对 v1.0 合约文件做内容 hash 或关键字段校验），把「不推翻已认证架构」变成机器可验证的性质。
3. **CERTIFICATION.md**：Phase 1 完成后在验证快照追加 smart-hardware fixture 一行；`CERTIFIED_DRY_RUN` 判定标准不变（全部测试绿）。Phase 4 前，production gate 行保持 `BLOCKED`。
4. **CI**：`.github/workflows/certify.yml` 无需改动（unittest discover 自动纳入新测试文件）。

---

## 9. 求职作品集叙事 + 公司使用方式

### 9.1 作品集叙事建议（展示设计能力的讲法）

1. **讲抽象层选择**：同一条 spine 承载三个完全不同的域（工业 3DP、时尚 SaaS、智能硬件外贸），只换 adapter 与政策文件——证明「域知识进 adapter，安全语义进 runtime」的分层判断。
2. **讲形态决策而非工具堆砌**：拿出 `decision-matrix.md`，说明为什么否决了「自主 SDR Agent」这个更炫的选项——面试官看重的是敢于给能力设边界的工程判断。
3. **讲对称的证据纪律**：product-intake 把 provenance 要求从「对客户的判断」延伸到「对自己产品的声明」（`CLAIMED_UNVERIFIED` 不得外泄）——这是原创设计点，一句话能讲清。
4. **讲 fail-closed 的可验证化**：「不破坏已认证架构」不是口号，而是一条 v1.0 冻结回归测试（§8.2）。
5. **讲 Wide early / Strict late** 在外贸域的实例化：多源族扩召回（海关+展会+认证库）在前，六个非补偿性合规硬门槛在后。

### 9.2 公司使用方式建议

- **销售/BD 日常**：通过 foreign-trade skill 的各 mode 做产品档案维护、客户研究、话术包生成；所有输出带 provenance，可直接进人审。
- **管理层**：用 Qualification 的 action class 分布与 Measurement 漏斗做管线复盘；attribution ≠ causality 的纪律防止错误归因驱动的策略摇摆。
- **合规**：Execution 政策文件是唯一外发闸门，合规团队只需评审政策文件与 suppression 流程，无需逐条审消息。
- **新品类扩张**：复制 smart-hardware adapter 模板（§4 结构）即可上新品类，spine 与 Skill 不动。

---

## 10. 下一个执行 Agent 的启动提示（Resume Prompt）

完整版（含逐文件 checklist）见 `next-agent-brief.md`。短版：

> Continue OnistAgentWorkflow from the certified v1.0 dry-run state. Read `PROJECT.md`, `cache/recovery-packet.md`, then `docs/upgrade-plans/foreign-trade-smart-hardware-v1.md` and `docs/upgrade-plans/next-agent-brief.md`. Execute Phase 1 of the upgrade plan: create the `skills/foreign-trade-lead-gen` skill, the `SMART_HARDWARE_IOT_EXPORT` adapter, v1.1 additive contracts, the smart-hardware dry-run example, and the new contract tests — without modifying any v1.0 contract, workflow, or existing test assertion. All work stays dry-run; live outreach remains BLOCKED. Acceptance: `python3 -m unittest discover -s tests -v` fully green including the new v1.0-freeze regression test.
