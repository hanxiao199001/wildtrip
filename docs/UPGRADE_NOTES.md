# 升级与治理说明（2026-08-28）

本次为保守治理，不做大重构。分支：`upgrade/2026-08-28`。

## 1. 依赖升级

| 依赖 | 旧版本 | 新版本 | 说明 |
|------|--------|--------|------|
| openai | 1.68.0 | 3.5.0 | 代码使用 `openai.OpenAI` + `chat.completions.create`，v1→v3 接口兼容，无需改代码 |
| chromadb | 0.4.22 | 1.5.9 | 见下 |
| httpx | 0.27.2 | 0.28.1 | openai 3.x 需要 |
| numpy | 1.26.4 | 2.2.6 | chromadb 1.x 依赖链要求 |
| APScheduler | （缺失） | 3.10.4 | `weekend_push_service` 一直在用但没进 requirements |

### chromadb 0.4 → 1.5 适配点

- 项目本来就用 `PersistentClient` + collection 级 API（`add/query/get/count/delete_collection`），
  在 1.5.9 下实测全部兼容（含 `$and` where 过滤、`list_collections()` 返回 Collection 对象）。
- `rag_engine.py` 的 `_get_or_create_collection` 从 `try get / except create`
  改为官方 `client.get_or_create_collection()`（1.x 中 get 失败抛 `NotFoundError`，裸 except 不可靠）。
- collection 命名要求 3–512 字符，现有名称 `travel_guides` 合规。
- 默认 embedding（ONNX MiniLM）首次使用需联网下载模型；离线环境请显式传入 embedding。
- **旧库数据**：仓库里 `backend/data/chroma_db/` 只有 HNSW 二进制分片，没有 `chroma.sqlite3`，
  本来就是不完整的库。升级后建议直接删掉旧目录、用 `backend/scripts/generate_history_data.py --import-only` 重新灌入。

## 2. 密钥治理

已移除/脱敏的硬编码：

- `backend/services/taobao_affiliate.py`：聚推客 API key 硬编码默认值 → 改为 `JUTUIKE_API_KEY` 环境变量（兼容历史拼写 `JUTULKE_API_KEY`）；`pub_id` 同理。
- `backend/tests/manual/test_jutulke_api.py`：同上，改读环境变量。
- `backend/saas/webhook/wechat_handler.py`：微信 token 写死 → `WECHAT_SAAS_TOKEN` 环境变量。
- `docs/guides/问题修复报告-小程序Mock数据.md`：文档中泄露的真实 DashScope key 已脱敏。

⚠️ **上述 key 已经进过 git 历史，视为已泄露**：请到 DashScope / 聚推客后台**吊销并重新生成**。

`.env.example` 已补充：`JUTUIKE_API_KEY`、`JUTUIKE_PUB_ID`、`FLASK_SECRET_KEY`、`WECHAT_SAAS_TOKEN`、`CHROMA_DB_PATH`。

## 3. JSON 存储收敛与数据库迁移方案

### 现状

JSON/JSONL 当轻量数据库，本次把散落的读写收敛到 **`backend/services/json_storage.py`**
（原子写入 + 进程内锁 + 统一容错），已接入：

- `services/guide_history_service.py`（用户攻略历史，`data/user_guides/<user_id>.json`）
- `api/track.py`（点击日志，`data/clicks/<date>.jsonl`）
- `api/guides.py` / `services/analytics_dashboard.py`（`metadata.json` 读取）

bots/scripts 里的一次性脚本读写暂未强制迁移（低风险）。
订单数据已经是 SQLite（`Flask-SQLAlchemy`，`data/orders.db`），无需处理。

### 迁移方案（建议上线前完成）

**阶段一：SQLite（推荐先做，半天工作量）**

1. 建表：`user_guides(guide_id PK, user_id, query, mode, content, stats_json, seo_url, favorite, created_at)`、
   `clicks(id PK, page, poi_name, poi_type, url, ip, ua, created_at)`、`guide_metadata(slug PK, ...)`。
2. 复用现有 `Flask-SQLAlchemy`（已初始化 `orders.db`），新增 model 即可。
3. 写一次性导入脚本遍历 `data/user_guides/*.json` 与 `data/clicks/*.jsonl` 灌库。
4. `GuideHistoryService` 保持接口不变，内部换成 ORM —— 调用方零改动（这正是本次收敛的目的）。

**阶段二：Supabase（多实例部署/需要 Auth 时再上）**

1. Postgres 表结构同上；用 `supabase-py`，连接串放 `SUPABASE_URL` / `SUPABASE_KEY`。
2. 手机号登录可顺势换成 Supabase Auth（现在的 `users.json` 明文存手机号，不合规）。
3. 点击日志量大，建议开 RLS + 按月分区，或直接走 Supabase 的 `pg_cron` 聚合。

## 4. 返佣现状（诚实声明）

**返佣未真实对接。** 现状：

- 链接只是拼接了 PID 参数的美团搜索页/中转页（`/api/relay/meituan`），无订单归因、无佣金回调、无结算，用户拿不到返现。
- `affiliate_manager.py` 里 `hotel_status = 'approved'` 等状态是写死的，不代表真实开通。
- 聚推客（淘宝联盟）有 API 封装但未验证真实出单。

**美团联盟对接待办：**

- [ ] 注册美团联盟 media 账号，完成主体资质审核（需营业执照）
- [ ] 申请对应类目（酒店/到店餐饮/门票）的推广权限，获取正式 `appkey/secret`
- [ ] 用官方 API 换取真实推广链接（deeplink/H5），替换现在手工拼接的搜索页 URL
- [ ] 实现订单查询/回调接口，把订单归因到 `sid`（用户维度的 sub-id）
- [ ] 设计返现台账 + 提现流程（涉及对用户付款，需考虑合规与个税）
- [ ] 小程序内跳转美团需使用 `navigateToMiniProgram`，确认 appId 白名单与场景值
- [ ] 在 README/前端明确披露佣金关系（广告法要求）

## 5. 大文件与不该入库的内容（未删除，仅列出）

**当前工作区：**

| 路径 | 大小 | 问题 |
|------|------|------|
| `web/guides/`（128 个 HTML） | 3.4 MB | 运行时生成产物，应由服务器生成/OSS 托管，不入库 |
| `web/dongpo-images.tar.gz` | 1.1 MB | 压缩包，且 `.gitignore` 已排除 `*.tar.gz`（入库早于规则） |
| `backend/data/chroma_db/*/*.bin` | 288 KB | 向量库二进制分片（且缺 sqlite 主文件，已损坏），应整目录忽略 |
| `data/users/users.json`、`user_guides.json` | 12 KB | **真实用户数据（手机号）入库，隐私风险，优先处理** |
| `backend/data/daily_reports/`、`daily_topics/` | 小 | 运行产物，不应入库 |

**git 历史中的历史包袱（已删文件仍占 pack，约 12 MB）：**

- `茶马古道攻略配图.tar.gz`（6.3 MB）、`茶马古道重点配图.tar.gz`（2.2 MB）——已从工作区删除但历史仍在。

**处理建议**（需仓库 owner 决策后另行执行）：`git rm --cached` 移出上述运行产物并补 `.gitignore`；
如要彻底瘦身/清除泄露密钥，用 `git filter-repo` 重写历史后 force-push（协作者需重新 clone）。

## 6. 测试

- 新增 `tests/conftest.py` + `tests/test_smoke.py`（15 个用例）：核心模块 import、
  json_storage 读写/JSONL 容错、攻略历史 CRUD、路径穿越防护、content_parser 纯函数。
- 运行：`pip install -r backend/requirements.txt pytest && pytest tests/test_smoke.py -v`
