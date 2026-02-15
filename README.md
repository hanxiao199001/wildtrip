# 野游记 WildTrip

> **不走寻常路，就走野路子**
> AI 驱动的旅游攻略生成器 + 预订返现平台

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![AI](https://img.shields.io/badge/AI-Qwen%2FDeepSeek-orange.svg)](https://www.deepseek.com/)
[![WeChat MiniProgram](https://img.shields.io/badge/小程序-微信-green.svg)](https://mp.weixin.qq.com/)

---

## 项目简介

**野游记（WildTrip）** 是一个面向自由行旅客的 AI 攻略生成工具。用户输入一句话（如"成都 3 天美食游，预算 2000"），系统在 30 秒内生成一篇 3000-5000 字的完整攻略，包含逐日行程、餐厅酒店推荐、预算明细和省钱贴士，并嵌入美团预订链接实现 50% 佣金返现。

项目同时提供 **微信小程序** 和 **Web 端** 两种前端，后端基于 Flask 异步生成 + WebSocket 实时推送。

### 核心特点

| 能力 | 说明 |
|------|------|
| 一句话生成 | 不用多轮对话，说清"去哪、几天、预算"即可 |
| 30 秒出稿 | Qwen/DeepSeek 模型驱动，单次成本约 ¥0.01 |
| 本地化推荐 | 基于 RAG 知识库推荐本地人去的餐厅和景点 |
| 预订返现 | 攻略内嵌美团链接，订单佣金 50% 返还用户 |
| 多模式生成 | 完整攻略 / 酒店推荐 / 美食推荐 / 历史人文 |
| 隐私保护 | 自动检测并脱敏用户输入中的手机号、身份证等 |
| SEO 获客 | 自动生成静态 HTML 攻略页，带 sitemap 和结构化数据 |

### 解决的痛点

| 传统方式 | 野游记 |
|---------|--------|
| 马蜂窝/小红书翻攻略，耗时长 | AI 生成，30 秒搞定 |
| OTA 平台预订，佣金不透明 | 美团预订，返现 50% |
| 千篇一律网红店推荐 | RAG 驱动本地化推荐 |
| ChatGPT 多轮对话，格式散乱 | 一句话输入，结构化输出 |

---

## 技术架构

```
┌──────────────────────────────────────────┐
│         微信小程序 / Web 前端             │
│   输入需求 → 实时进度 → 查看攻略         │
└────────────────┬─────────────────────────┘
                 │ HTTP / WebSocket
┌────────────────┴─────────────────────────┐
│          Flask API 后端 (port 5000)      │
│  任务管理 │ 进度推送 │ 数据处理 │ SEO    │
└───┬────────┬──────────┬──────────┬───────┘
    │        │          │          │
┌───┴────┐ ┌─┴──────┐ ┌┴────────┐ ┌┴──────────┐
│Qwen /  │ │聚推客  │ │ChromaDB │ │JSON 文件  │
│DeepSeek│ │返佣链接│ │RAG 知识库│ │用户/攻略  │
└────────┘ └────────┘ └─────────┘ └───────────┘
```

### 技术栈

**后端**
- Python 3.10+ / Flask + Flask-SocketIO
- Qwen3-Max / DeepSeek API（AI 攻略生成，约 ¥0.01/次）
- 聚推客 API（美团 CPS 返佣链接生成）
- ChromaDB（RAG 语义检索知识库）
- JSON 文件存储（用户账户、攻略记录）
- Loguru（日志管理）

**前端**
- 微信小程序原生开发（主入口）
- Web H5（备用入口，Tailwind CSS）
- WebSocket 实时进度 + 轮询降级

**部署**
- Nginx 反向代理（端口 8080 → 5000）
- 静态 HTML 攻略页自动生成

---

## 快速开始

### 环境要求

- Python 3.10+
- 微信开发者工具（小程序开发，可选）

### 1. 克隆项目

```bash
git clone https://github.com/hanxiao199001/wildtrip.git
cd wildtrip
```

### 2. 后端启动

```bash
cd backend
cp .env.example .env
# 编辑 .env，填入 AI API Key
pip install -r requirements.txt
python3 app.py
# 服务运行在 http://localhost:5000
```

**获取 API Key：**
- **Qwen（推荐）：** 访问 https://dashscope.aliyun.com 注册获取
- **DeepSeek：** 访问 https://platform.deepseek.com 注册获取

将 Key 填入 `.env` 的 `AI_API_KEY` 字段。

### 3. 前端启动

**Web 端：**
```bash
cd web
python3 -m http.server 8080
# 访问 http://localhost:8080
```

**小程序：**
1. 打开微信开发者工具
2. 导入 `miniprogram/` 目录
3. 修改 `app.js` 中的 `apiBaseUrl` 为后端地址

### 4. 测试

```bash
# 创建生成任务
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"query":"海口3天亲子游，预算5000","mode":"full"}'

# 查询任务状态（用返回的 task_id）
curl http://localhost:5000/api/task/<task_id>
```

---

## 项目结构

```
wildtrip/
├── backend/                        # Flask 后端服务
│   ├── app.py                      # 主应用入口
│   ├── requirements.txt            # Python 依赖
│   ├── .env.example                # 环境变量模板
│   ├── api/                        # API 路由层
│   │   ├── generate.py             # 攻略生成 API
│   │   ├── guides.py               # 攻略列表 / CRUD
│   │   ├── user.py                 # 用户登录 / 历史
│   │   ├── clarify.py              # 需求澄清（多轮）
│   │   └── qrcode.py              # 小程序码生成
│   ├── services/                   # 核心业务逻辑
│   │   ├── ai_engine.py            # AI 模型封装
│   │   ├── ai_engine_streaming.py  # 流式 AI 生成
│   │   ├── rag_engine.py           # RAG 语义检索
│   │   ├── affiliate.py            # 返佣链接生成
│   │   ├── affiliate_manager.py    # 返佣管理
│   │   ├── jutuike_api.py          # 聚推客 API 封装
│   │   ├── need_analyzer.py        # 用户需求解析
│   │   ├── need_clarifier.py       # 多轮需求澄清
│   │   ├── privacy_cleaner.py      # 隐私信息脱敏
│   │   ├── seo_service.py          # SEO 静态页生成
│   │   ├── seo_optimizer.py        # SEO 优化
│   │   ├── itinerary_generator.py  # 行程生成器
│   │   ├── clean_html_generator.py # HTML 模板生成
│   │   ├── image_crawler.py        # 图片抓取
│   │   └── user_service.py         # 用户数据管理
│   ├── prompts/                    # AI Prompt 模板
│   │   ├── wildtrip_prompt.py      # 主攻略 Prompt
│   │   └── history_culture_prompt.py # 历史人文模式 Prompt
│   ├── data/chroma_db/             # ChromaDB 向量数据库
│   └── logs/                       # 运行日志
│
├── miniprogram/                    # 微信小程序前端
│   ├── app.js / app.json / app.wxss
│   ├── pages/
│   │   ├── index/                  # 首页（需求输入）
│   │   ├── clarify/                # 需求澄清页
│   │   ├── generate/               # 生成页（进度展示）
│   │   ├── result/                 # 结果页（攻略展示）
│   │   ├── guide-detail/           # 攻略详情页
│   │   ├── cashback/               # 返现说明
│   │   └── webview/                # WebView 容器
│   ├── utils/api.js                # API 封装 & WebSocket
│   └── towxml/                     # Markdown → WXML 解析
│
├── web/                            # Web H5 前端
│   ├── index.html                  # 主页面
│   ├── app.js                      # 前端逻辑
│   ├── guides/                     # 生成的静态攻略页（96 篇）
│   └── public/                     # 静态资源
│
├── scripts/                        # 工具脚本
│   ├── seo-batch-generate.js       # SEO 攻略页批量生成
│   ├── xiaohongshu-batch-generate.js # 小红书内容批量生成
│   ├── monitor-memory.sh           # 内存监控脚本
│   └── llt-login.js / llt-config.json # 登录测试工具
│
├── deploy/                         # 部署配置
│   └── nginx.conf                  # Nginx 反向代理配置
│
├── docs/                           # 项目文档
│   ├── 快速开始.md                  # 快速上手指南
│   ├── 返现机制设计.md              # 返现机制设计文档
│   ├── FRONTEND_DEV.md             # 前端开发指南
│   ├── seo/                        # SEO 相关文档
│   │   ├── SEO优化获客方案.md
│   │   ├── SEO优化完成报告.md
│   │   ├── SEO优化验证指南.md
│   │   └── SEO提交指南.md
│   ├── features/                   # 功能说明文档
│   │   ├── RAG系统演示文档.md
│   │   ├── 隐私保护功能说明.md
│   │   └── 图片支持升级-2026-02-05.md
│   ├── integrations/               # 第三方集成文档
│   │   ├── 美团搜索提示方案.md
│   │   ├── 美团返现配置指南.md
│   │   └── 百度统计配置说明.md
│   └── content/                    # 内容素材
│       └── 苏东坡被贬之路-公众号版.md
│
├── data/users/                     # 用户数据（JSON）
├── dongpo-images/                  # 苏东坡主题配图素材
├── xiaohongshu-content/            # 小红书分发内容
├── skills-content-formatter/       # 内容格式化工具
├── skills-image-fetcher/           # 图片自动下载工具
│
├── README.md                       # 项目说明（本文件）
├── CONTRIBUTING.md                 # 贡献指南
├── LICENSE                         # MIT 开源协议
└── project.config.json             # 微信小程序配置
```

---

## 核心功能

### 1. AI 攻略生成

用户输入一句话需求，系统自动解析城市、天数、预算、人群偏好，调用 AI 模型生成结构化攻略：

- **逐日行程规划**（精确到时间段）
- **餐厅推荐**（早中晚，含人均价格和评分）
- **酒店推荐**（3 档价位）
- **省钱 Tips** 和避坑指南
- **本地人玩法**（不走网红路线）

支持 4 种生成模式：

| 模式 | 说明 |
|------|------|
| `full` | 完整攻略（行程 + 酒店 + 餐厅 + 贴士） |
| `hotel` | 仅酒店推荐（快速模式） |
| `food` | 仅美食推荐（快速模式） |
| `history` | 历史人文主题攻略 |

### 2. RAG 知识库

基于 ChromaDB 向量数据库，存储已有攻略的语义向量。生成新攻略时，先检索相似内容作为上下文注入 AI Prompt，确保推荐的餐厅、景点真实可靠，有效防止 AI 幻觉。

### 3. 智能需求澄清

用户输入模糊需求时，系统自动提出补充问题（出行天数、预算范围、人群类型、偏好等），多轮对话优化攻略质量。API 不可用时自动降级为前端本地问题模板。

### 4. 美团返佣

攻略中的酒店、餐厅、景点名称自动生成带返佣参数的美团搜索链接。用户通过链接预订后，佣金的 50% 返还给用户。通过聚推客 API 实现订单归因追踪。

### 5. 隐私保护

PrivacyCleaner 模块自动检测用户输入中的手机号、身份证号、银行卡号、邮箱、车牌号等 10+ 类敏感信息，在保存公开页面前脱敏处理。

### 6. SEO 获客

每篇攻略自动生成独立的静态 HTML 页面，包含 meta 标签、JSON-LD 结构化数据和 Open Graph 标记，通过 sitemap.xml 提交搜索引擎收录。目前已生成 96+ 篇攻略页。

---

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/generate` | 创建攻略生成任务 |
| GET  | `/api/task/<task_id>` | 查询任务进度和结果 |
| GET  | `/api/guides` | 攻略列表 |
| GET  | `/api/guides/<slug>` | 获取单篇攻略 |
| POST | `/api/user/login` | 手机号登录 |
| GET  | `/api/user/<id>/guides` | 用户攻略历史 |
| POST | `/api/clarify` | 多轮需求澄清 |
| POST | `/api/qrcode` | 生成小程序码 |
| GET  | `/api/health` | 健康检查 |

WebSocket 事件：`/socket.io` 实时推送生成进度。

---

## 商业模式

**收入来源：** 美团联盟佣金分成（酒店 5-15%、餐饮 8-20%、门票 10-25%），50% 返给用户，50% 作为平台收入。

**运营成本：** 服务器 ¥200/月 + AI API ¥100/月 = ¥300/月，约 20-30 笔订单可覆盖。

**未来规划：** 会员订阅（¥19.9/月无限生成）、B 端 SaaS API。

---

## Roadmap

- [x] 后端 API + AI 攻略生成
- [x] 微信小程序前端
- [x] Web H5 前端
- [x] 美团返佣链接嵌入
- [x] RAG 知识库
- [x] SEO 静态页 + sitemap
- [x] 隐私保护脱敏
- [x] 用户系统（手机号登录）
- [x] 需求澄清多轮对话
- [x] 历史人文模式
- [x] 分享海报功能
- [ ] 真机测试 + 用户反馈
- [ ] 美团真实返佣对接
- [ ] 订单跟踪 + 自动结算
- [ ] 小程序正式上线

---

## 文档导航

| 分类 | 文档 | 说明 |
|------|------|------|
| 入门 | [快速开始](docs/快速开始.md) | 环境搭建与首次运行 |
| 入门 | [前端开发指南](docs/FRONTEND_DEV.md) | 前端开发说明 |
| 入门 | [贡献指南](CONTRIBUTING.md) | 如何参与贡献 |
| 功能 | [RAG 系统演示](docs/features/RAG系统演示文档.md) | RAG 知识库使用说明 |
| 功能 | [隐私保护说明](docs/features/隐私保护功能说明.md) | 隐私脱敏机制 |
| 功能 | [图片支持升级](docs/features/图片支持升级-2026-02-05.md) | 图片功能更新说明 |
| SEO | [SEO 获客方案](docs/seo/SEO优化获客方案.md) | SEO 整体策略 |
| SEO | [SEO 完成报告](docs/seo/SEO优化完成报告.md) | SEO 优化成果 |
| SEO | [SEO 验证指南](docs/seo/SEO优化验证指南.md) | SEO 效果验证 |
| SEO | [SEO 提交指南](docs/seo/SEO提交指南.md) | 搜索引擎提交步骤 |
| 集成 | [美团搜索方案](docs/integrations/美团搜索提示方案.md) | 美团搜索集成方案 |
| 集成 | [美团返现配置](docs/integrations/美团返现配置指南.md) | 返现配置步骤 |
| 集成 | [百度统计配置](docs/integrations/百度统计配置说明.md) | 百度统计接入 |
| 设计 | [返现机制设计](docs/返现机制设计.md) | 返现业务逻辑设计 |

---

## 开源协议

[MIT License](LICENSE)

---

**项目负责人：** Zero & 老韩
**GitHub：** https://github.com/hanxiao199001/wildtrip
**问题反馈：** [提交 Issue](https://github.com/hanxiao199001/wildtrip/issues)
