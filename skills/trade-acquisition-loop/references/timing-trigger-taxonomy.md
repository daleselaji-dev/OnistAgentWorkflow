# 时机触发分类(Timing Trigger Taxonomy)

规范源:`contracts/timing-trigger-taxonomy-v1.0.json`。核心思想:**"什么时候"决定"找谁"** —— 用带日期、带证据的触发事件排序获客队列,而不是静态 ICP 名单。

## 十个触发族速查

| 触发族 | 观察什么 | 新鲜窗口 | 权重 | 3DP 例子 | CLO 例子 |
|---|---|---|---|---|---|
| HIRING_SIGNAL | 会使用/负责该能力的岗位招聘 | 60d | 0.8 | 招增材/工装/工艺工程师 | 招 3D 设计师/CLO artist |
| EXPANSION | 新厂/新线/新办公室/新市场 | 120d | 0.7 | 新产线→新治具需求 | 新设计团队→协作负载 |
| TRADE_SHOW | 参展商/观展名录 | 45d(展前30/展后14) | 0.9 | Formnext/TCT 参展 | Kingpins/PV/ISPO 参展 |
| REGULATORY | 改变现流程成本的法规 | 180d | 0.6 | 部件认证/本地化要求 | 数字产品护照/溯源 |
| TECH_STACK_SHIFT | 相邻/前置技术采纳 | 90d | 0.7 | CAD/PLM 现代化 | 引擎/管线升级需布料资产 |
| COMPETITOR_MOVE | 同行公开采纳同类能力 | 120d | 0.5 | 竞对自建工装打印 | 竞对 3D 减样 |
| FUNDING_CAPEX | 融资/资本开支/预算周期 | 180d | 0.6 | 产线现代化 capex | 设计组织扩张融资 |
| LEADERSHIP_CHANGE | 决策相关角色到任 | 90d | 0.6 | 新制造工程负责人 | 新产品开发 VP |
| SUPPLY_CHAIN_EVENT | 断供/回流/供应商交期危机 | 90d | 0.8 | 外协工装交期爆炸 | 实物样衣物流瓶颈 |
| NEW_PRODUCT_LAUNCH | 消耗该能力的新产品线 | 120d | 0.7 | 新 SKU 族工装爬坡 | 新剧/新游戏需服装资产 |

## 激活规则(代码强制,`score_timing_triggers`)

- 每个触发必须是证据台账里的 claim:`trigger_id + observed_day + evidence_ref`,**无日期/无证据不得激活外呼**。
- `score = Σ(权重 × 新鲜度)`;新鲜度在窗口内为 1,窗口外为 0。
- `score ≥ 0.8` → OUTBOUND_NOW;`0.5–0.8` → DISCOVERY_OUTREACH;`< 0.5` → MONITOR_NURTURE。
- 触发分只排序队列,**永远不能翻转资格硬门禁**(技术封套 FAIL 就是 REJECT,分再高也没用)。
- 过期触发把 timing 降为 UNKNOWN,不是负面;fit-only 无触发的公司进 watchlist 监控,不冷呼。

## 调研配方

对每个 adapter:`(job-to-be-done 关键词) × (触发族信号源) × (territory 语言)`。
展会名录与招聘源同时是 Discovery 的 source family——触发监控与 universe 构建共享同一套采集基础设施,一次投入两处收益。

## 与主 workflow 的接线

1. Discovery 阶段:触发源作为 source family 之一,产出候选 + 触发线索。
2. Evidence 阶段:触发线索验证成带日期的 claim。
3. Qualification 阶段:触发分映射 timing/intent 维度,输出 action class 建议档位。
4. Learning 阶段:触发→成交的转化率按触发族统计,C2+ 证据才能调整权重(权重是全局策略)。
