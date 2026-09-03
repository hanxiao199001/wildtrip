# 野游记 WildTrip

> **不走寻常路，就走野路子**
> AI 驱动的旅游攻略生成器 + 预订返现平台

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![DeepSeek](https://img.shields.io/badge/AI-DeepSeek-orange.svg)](https://www.deepseek.com/)
[![WeChat MiniProgram](https://img.shields.io/badge/小程序-微信-green.svg)](https://mp.weixin.qq.com/)

---

## 项目简介

**野游记（WildTrip）** 是一个面向自由行旅客的 AI 攻略生成工具。用户输入一句话（如"成都 3 天美食游，预算 2000"），系统在 30 秒内生成一篇 3000–5000 字的完整攻略，包含逐日行程、餐厅酒店推荐、预算明细和省钱贴士，并嵌入美团预订链接（返佣为规划功能，**尚未真实对接美团联盟**，详见 docs/UPGRADE_NOTES.md）。

项目同时提供 **微信小程序** 和 **Web 端** 两种前端，后端基于 Flask 异步生成 + WebSocket 实时推送。

### 核心特点

| 能力 | 说明 |
|------|------|
| 一句话生成 | 不用多轮对话，说清"去哪、几天、预算"即可 |
| 30 秒出稿 | DeepSeek 模型驱动，单次成本约 ¥0.01 |
| 本地化推荐 | 基于 RAG 知识库推荐本地人去的餐厅和景点 |
| 预订返现 | 攻略内嵌美团链接（⚠️ 返佣未真实对接，暂无实际返现） |
| 隐私保护 | 自动检测并脱敏用户输入中的手机号、身份证等 |
| SEO 获客 | 自动生成静态 HTML 攻略页，带 sitemap 和结构化数据 |

### 解决的痛点

| 传统方式 | 野游记 |
|---------|--------|
| 马蜂窝/小红书翻攻略，耗时长 | AI 生成，30 秒搞定 |
| OTA 平台预订，佣金不透明 | 美团预订，返现 50%（规划中，未上线） |
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
│DeepSeek│ │美团 API│ │ChromaDB │ │JSON 文件  │
│AI 生成 │ │返佣链接│ │RAG 知识库│ │用户/攻略  │
└────────┘ └────────┘ └─────────┘ └───────────┘
```

### 技术栈

**后端**
- Python 3.10+ / Flask + Flask-SocketIO
- DeepSeek API（AI 攻略生成）
- 美团联盟 API（返佣链接生成）
- ChromaDB（RAG 语义检索知识库）
- JSON 文件存储（用户账户、攻略记录）

**前端**
- 微信小程序原生开发（主入口）
- Web H5（备用入口，Tailwind CSS）
- WebSocket 实时进度 + 轮询降级

**AI 核心**
- 模型：DeepSeek Chat
- 成本：约 ¥0.01/次
- 速度：20–30 秒生成 4000+ 字

---

## 快速开始

### 环境要求

- Python 3.10+
- 微信开发者工具（小程序开发）

### 1. 克隆项目

```bash
git clone https://github.com/hanxiao199001/wildtrip.git
cd wildtrip
```

### 2. 后端启动

```bash
cd backend
cp .env.example .env
# 编辑 .env，填入 DeepSeek API Key
pip install -r requirements.txt
python3 app.py
# 服务运行在 http://localhost:5000
```

**获取 DeepSeek API Key：**
1. 访问 https://platform.deepseek.com
2. 注册并创建 API Key
3. 填入 `.env` 的 `AI_API_KEY` 字段

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
├── backend/                        # Flask 后端
│   ├── app.py                      # 主应用入口
│   ├── requirements.txt            # Python 依赖
│   ├── .env.example                # 环境变量模板
│   ├── api/                        # API 路由
│   │   ├── generate.py             # 攻略生成 API
│   │   ├── guides.py               # 攻略列表 / CRUD
│   │   └── user.py                 # 用户登录 / 历史
│   ├── services/                   # 核心业务逻辑
│   │   ├── ai_engine.py            # DeepSeek AI 封装
│   │   ├── itinerary_generator.py  # 行程生成器
│   │   ├── rag_engine.py           # RAG 语义检索
│   │   ├── affiliate.py            # 美团返佣链接
│   │   ├── affiliate_manager.py    # 返佣管理
│   │   ├── meituan_api.py          # 美团 API 封装
│   │   ├── seo_service.py          # SEO 静态页生成
│   │   ├── user_service.py         # 用户数据管理
│   │   ├── need_analyzer.py        # 用户需求解析
│   │   ├── image_crawler.py        # 图片抓取
│   │   ├── privacy_cleaner.py      # 隐私脱敏
│   │   └── clean_html_generator.py # HTML 模板生成
│   ├── prompts/                    # AI Prompt 模板
│   │   └── wildtrip_prompt.py
│   ├── data/chroma_db/             # ChromaDB 向量数据库
│   └── logs/                       # 运行日志
│
├── miniprogram/                    # 微信小程序前端
│   ├── app.js / app.json / app.wxss
│   ├── pages/
│   │   ├── index/                  # 首页（需求输入）
│   │   ├── generate/               # 生成页（进度展示）
│   │   ├── result/                 # 结果页（攻略展示）
│   │   ├── cashback/               # 返现说明
│   │   └── webview/                # WebView 容器
│   ├── utils/api.js                # API 封装
│   └── towxml/                     # Markdown → WXML 解析
│
├── web/                            # Web 前端
│   ├── index.html                  # 主页面
│   ├── app.js                      # 前端逻辑
│   ├── guides/                     # 生成的静态攻略页（96 篇）
│   └── public/                     # 静态资源
│
├── data/users/                     # 用户数据（JSON）
│   ├── users.json                  # 用户账户
│   └── user_guides.json            # 用户攻略记录
│
├── docs/                           # 文档
│   ├── 快速开始.md
│   └── 返现机制设计.md
│
├── README.md
├── FRONTEND_DEV.md                 # 前端开发指南
├── CONTRIBUTING.md                 # 贡献指南
├── LICENSE                         # MIT
└── nginx.conf                      # Nginx 反向代理配置
```

---

## 核心功能

### 1. AI 攻略生成

用户输入一句话需求，系统自动解析城市、天数、预算、人群偏好，调用 DeepSeek 生成结构化攻略：

- 逐日行程规划（精确到时间段）
- 餐厅推荐（早中晚，含人均价格和评分）
- 酒店推荐（3 档价位）
- 省钱 Tips 和避坑指南
- 本地人玩法（不走网红路线）

生成内容自动插入美团预订链接，保存为可分享的静态 HTML 页面。

### 2. RAG 知识库

基于 ChromaDB 向量数据库，存储已有攻略的语义向量。生成新攻略时，先检索相似内容作为上下文注入 AI Prompt，确保推荐的餐厅、景点真实可靠。

### 3. 美团返佣（⚠️ 尚未真实对接）

> **诚实声明：** 返佣目前只是"链路演示"。攻略中的酒店/餐厅/景点会生成带返佣参数的美团搜索链接（经 `/api/relay/meituan` 中转页），但**未完成美团联盟的正式对接**——没有真实的 CPS 订单归因，也没有佣金结算，用户实际拿不到返现。待办清单见 `docs/UPGRADE_NOTES.md`。

### 4. 隐私保护

PrivacyCleaner 模块自动检测用户输入中的手机号、身份证、邮箱等敏感信息，在保存公开页面前脱敏处理。

### 5. SEO 获客

每篇攻略自动生成独立的静态 HTML 页面，包含 meta 标签、JSON-LD 结构化数据和 Open Graph 标记，通过 sitemap.xml 提交搜索引擎收录。

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

WebSocket 事件：`/socket.io` 实时推送生成进度。

---

## 商业模式

**收入来源（规划中，未实现）：** 美团联盟佣金分成（酒店 5–15%、餐饮 8–20%、门票 10–25%），50% 返给用户，50% 作为平台收入。**当前返佣链路未真实对接，实际收入为 0**，详见 `docs/UPGRADE_NOTES.md`。

**运营成本：** 服务器 ¥200/月 + AI API ¥100/月 = ¥300/月，约 20–30 笔订单可覆盖。

**未来规划：** 会员订阅（¥19.9/月无限生成）、B 端 SaaS API。

---

## Roadmap

- [x] 后端 API + AI 攻略生成
- [x] 微信小程序前端
- [x] Web H5 前端
- [x] 美团返佣链接嵌入（仅链接拼接，未产生真实佣金）
- [x] RAG 知识库
- [x] SEO 静态页 + sitemap
- [x] 隐私保护脱敏
- [x] 用户系统（手机号登录）
- [ ] 真机测试 + 用户反馈
- [ ] 美团真实返佣对接
- [ ] 订单跟踪 + 自动结算
- [ ] 小程序正式上线

---

## 贡献

欢迎贡献代码，详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 开源协议

[MIT License](LICENSE)

---

**项目负责人：** Zero & 老韩
**GitHub：** https://github.com/hanxiao199001/wildtrip
**问题反馈：** [提交 Issue](https://github.com/hanxiao199001/wildtrip/issues)
