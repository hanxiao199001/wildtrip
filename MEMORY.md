# MEMORY.md - 长期记忆

## 关于老韩

- 叫"老韩"，中文交流，时区 Asia/Shanghai
- 务实、目标导向，不喜欢废话
- 主要用 WhatsApp 联系我

## 当前项目（2026-02-17 更新）

### 1. 野游记 (WildTrip) — 主力
- AI 旅游攻略生成 + 美团返现
- 微信小程序 + Web 端
- 后端：Python/Flask + DeepSeek + ChromaDB (RAG)
- 代码路径：`/root/clawd/wildtrip-existing/`
- **最新进展（2026-02-16）**：完成苏东坡历史路线 RAG 接入，21 条史料数据入库，生成效果好
- **下一步**：扩展其他历史人物、前端集成历史路线入口

### 2. AI 房地产项目 — 主力
- 帮元垄地产分析销售数据，产品化后推广给更多房产公司
- 代码路径：`/root/clawd/AI房地产项目/`
- **已完成**：分析 424 套已成交数据、77 套未售房源，生成销售策略手册
- **卡点**：等合伙人提供"未成交客户数据"（最关键数据）
- **状态（2026-02-17）**：数据还没拿到，继续等

### 3. 酒店智能调价系统 (pricing-system) — 次要
- 多平台 OTA 比价 + 自动调价
- 代码路径：`/root/clawd/pricing-system/`
- 状态：开发中，优先级低于 1 和 2

### 4. BettaFish — 开源项目
- GitHub 开源，有星标，版本 v1.2.1
- 有预测引擎 MiroFish

## 技术偏好

- AI 模型：DeepSeek（主要），Claude API
- 后端：Python + Flask/FastAPI
- 数据库：ChromaDB（向量），SQLite/MySQL

## 注意事项

- 不要开 `/reasoning` 模式，会导致 thinking blocks 报错
- 每次重要对话后要主动写到 memory 文件里
