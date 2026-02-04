# 🔥 野游记 WildTrip

> **不走寻常路，就走野路子**  
> AI驱动的旅游攻略生成器 + 预订返现平台

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![DeepSeek](https://img.shields.io/badge/AI-DeepSeek-orange.svg)](https://www.deepseek.com/)
[![WeChat MiniProgram](https://img.shields.io/badge/小程序-微信-green.svg)](https://mp.weixin.qq.com/)

---

## 📖 项目简介

**野游记（WildTrip）** 是一款AI驱动的旅游攻略生成工具，用30秒帮你生成完整的旅行攻略，并提供酒店/餐饮/门票的预订返现。

### 🎯 核心特点

- **🚀 30秒生成** - 一句话描述需求，AI自动生成3000+字完整攻略
- **💰 预订返现50%** - 通过美团预订酒店/餐饮/门票，返现50%佣金
- **😴 一句话搞定** - 不用多轮对话，说清楚"去哪、玩几天、预算多少"即可
- **🌍 本地化推荐** - 不推网红店，推本地人去的地方
- **📱 小程序体验** - 微信扫码即用，无需下载APP

### 💡 解决的痛点

| 传统方式 | 野游记 |
|---------|--------|
| ❌ 马蜂窝查攻略，5分钟+ | ✅ AI生成，30秒 |
| ❌ 携程预订，佣金20% | ✅ 美团预订，返现50% |
| ❌ 网红店排队，坑 | ✅ 本地人推荐，真 |
| ❌ 多轮对话，累 | ✅ 一句话搞定，爽 |

---

## 🖼️ 效果展示

### 生成效果示例

**输入：**
```
海口3天亲子游，预算5000
```

**输出：**
- 📄 4500+字完整攻略
- 🏨 1家酒店推荐（含预订链接）
- 🍽️ 3家餐厅推荐（本地特色）
- 🎫 2个景点门票（美团优惠价）
- 💰 预估返现：¥250

**攻略内容：**
- ✅ 详细行程规划（每天每小时）
- ✅ 餐厅推荐（早中晚餐）
- ✅ 酒店选择建议（3档价位）
- ✅ 省钱Tips（美团团购、避坑指南）
- ✅ 本地人玩法（不走网红路线）

---

## 🏗️ 技术架构

```
┌──────────────────────────────────────────┐
│           微信小程序（前端）              │
│   输入需求 → 实时进度 → 查看攻略         │
└────────────────┬─────────────────────────┘
                 │ HTTP/WebSocket
┌────────────────┴─────────────────────────┐
│           Flask API（后端）               │
│   任务管理 | 进度推送 | 数据处理          │
└────┬──────────┬──────────────┬───────────┘
     │          │              │
┌────┴─────┐ ┌──┴──────┐ ┌────┴────────┐
│ DeepSeek │ │ 美团API │ │ PostgreSQL  │
│ AI生成   │ │ 返佣链接│ │ 用户/订单   │
└──────────┘ └─────────┘ └─────────────┘
```

### 技术栈

**后端：**
- 🐍 Python 3.10+ / Flask
- 🤖 DeepSeek API (AI生成)
- 🔗 美团联盟API (返佣链接)
- 🗄️ PostgreSQL (数据存储)
- 🔌 Flask-SocketIO (实时进度)

**前端：**
- 📱 微信小程序原生开发
- 🎨 Perplexity薄荷绿风格
- ⚡ 实时轮询 + WebSocket

**AI核心：**
- 模型：DeepSeek Chat
- 成本：¥0.01/次（vs GPT-4 ¥0.7/次）
- 速度：20-30秒生成4000+字

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Node.js 16+ (可选，用于前端开发)
- 微信开发者工具

### 1. 克隆项目

```bash
git clone https://github.com/hanxiao199001/wildtrip.git
cd wildtrip
```

### 2. 后端配置

```bash
cd backend

# 复制配置文件
cp .env.example .env

# 编辑.env，填入API Key
# AI_API_KEY=你的DeepSeek_API_Key
nano .env

# 安装依赖
pip install -r requirements.txt

# 启动服务
python3 app.py

# 服务运行在 http://localhost:5000
```

**获取DeepSeek API Key：**
1. 访问：https://platform.deepseek.com
2. 注册账号
3. 创建API Key
4. 填入 `.env` 文件

### 3. 前端配置

```bash
# 打开微信开发者工具
# 导入项目目录：wildtrip/miniprogram
# AppID：使用测试号

# 修改API地址（如果需要）
# 编辑 miniprogram/app.js
# apiBaseUrl: 'http://你的服务器IP:5000/api'
```

### 4. 测试运行

**后端API测试：**
```bash
# 创建生成任务
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"query":"海口周末游","mode":"full"}'

# 返回：{"task_id": "xxx", "status": "started"}

# 查询任务状态
curl http://localhost:5000/api/task/xxx

# 返回：{"status": "completed", "result": {...}}
```

**前端测试：**
1. 打开小程序
2. 输入："海口3天亲子游，预算5000"
3. 点击生成
4. 等待30秒
5. 查看攻略

---

## 📁 项目结构

```
wildtrip/
├── README.md                    # 本文件
├── FRONTEND_DEV.md              # 前端开发指南
├── LICENSE                      # MIT协议
├── .gitignore                   # Git忽略文件
│
├── backend/                     # 后端服务
│   ├── app.py                   # Flask主应用
│   ├── .env.example             # 配置模板
│   ├── requirements.txt         # Python依赖
│   │
│   ├── api/                     # API路由
│   │   └── generate.py          # 攻略生成API
│   │
│   ├── services/                # 核心服务
│   │   ├── ai_engine.py         # DeepSeek AI封装
│   │   ├── affiliate.py         # 美团返佣链接生成
│   │   └── meituan_api.py       # 美团联盟API
│   │
│   └── prompts/                 # AI Prompt
│       └── wildtrip_prompt.py   # 攻略生成Prompt
│
├── miniprogram/                 # 微信小程序
│   ├── app.js                   # 全局配置
│   ├── app.json                 # 页面配置
│   ├── app.wxss                 # 全局样式
│   │
│   ├── pages/                   # 页面
│   │   ├── index/               # 首页（输入）
│   │   ├── generate/            # 生成页（进度）
│   │   ├── result/              # 结果页（攻略展示）
│   │   └── cashback/            # 返现说明
│   │
│   ├── utils/                   # 工具函数
│   │   └── api.js               # API封装
│   │
│   └── project.config.json      # 小程序配置
│
└── docs/                        # 文档
    ├── 快速开始.md
    └── 返现机制设计.md
```

---

## 🔧 核心功能详解

### 1. AI攻略生成

**Prompt工程：**
```python
# prompts/wildtrip_prompt.py

WILDTRIP_SYSTEM_PROMPT = """
你是"野游记 WildTrip"的AI旅游导游，slogan是"不走寻常路，就走野路子"。

你的特点：
1. 有态度 - 不推千篇一律的网红景点
2. 接地气 - 说人话，不官方腔
3. 实用主义 - 帮用户省钱省心
4. 有梗 - 幽默风趣

语言风格示例：
✅ "这家店巨好吃，本地人都去，别在网红店排队了"
❌ "该景点具有丰富的历史文化底蕴"（太官方）
"""
```

**生成流程：**
1. 用户输入 → 解析需求（城市、天数、预算、偏好）
2. 调用DeepSeek API → 生成攻略内容（4000+字）
3. 正则提取 → 酒店/餐厅/景点名称
4. 生成美团链接 → 插入攻略中
5. 返回前端 → 展示+复制+分享

### 2. 美团返佣链接

**工作原理：**
```python
# services/affiliate.py

def get_search_link(query, category='hotel'):
    """
    生成美团搜索链接（带返佣参数）
    
    Args:
        query: 搜索关键词（如"海口希尔顿酒店"）
        category: 类别（hotel/food/ticket）
    
    Returns:
        带返佣参数的美团链接
    """
    base_url = {
        'hotel': 'https://i.meituan.com/hotel/search',
        'food': 'https://i.meituan.com/search',
        'ticket': 'https://i.meituan.com/ticket/search'
    }[category]
    
    # 添加返佣参数（需要美团联盟AppKey）
    params = {
        'q': query,
        'sid': MEITUAN_SID,
        # ... 其他返佣参数
    }
    
    return f"{base_url}?{urlencode(params)}"
```

**返现流程：**
1. 用户点击攻略中的美团链接
2. 跳转到美团预订
3. 完成订单支付
4. 美团联盟结算佣金（7-30天）
5. 野游记返现50%给用户

### 3. 实时进度推送

**技术方案：**
- 轮询（Polling）：每2秒查询一次任务状态
- WebSocket（可选）：服务端主动推送进度

```javascript
// miniprogram/pages/generate/generate.js

async pollTaskStatus() {
  this.timer = setInterval(async () => {
    const status = await this.callAPI(`/task/${taskId}`, {}, 'GET')
    
    this.setData({ progress: status.progress })
    
    if (status.status === 'completed') {
      clearInterval(this.timer)
      this.onGenerateComplete(status.result)
    }
  }, 2000)  // 每2秒查询一次
}
```

---

## 💰 商业模式

### 收入来源

1. **美团联盟佣金** (主要)
   - 酒店预订：佣金5-15%
   - 餐饮团购：佣金8-20%
   - 门票预订：佣金10-25%
   - **返现50%给用户，留50%作为收入**

2. **会员订阅** (未来)
   - 免费版：每月3次生成
   - 会员版：¥19.9/月，无限生成

3. **B端SaaS** (未来)
   - 提供API给旅行社/OTA
   - 按量计费：¥0.5/次

### 成本结构

| 项目 | 成本 | 备注 |
|------|------|------|
| 服务器 | ¥200/月 | 阿里云ECS |
| AI API | ¥100/月 | DeepSeek（1万次调用） |
| 美团联盟 | ¥0 | 无接入成本 |
| **总计** | **¥300/月** | 初期成本 |

**盈亏平衡：**
- 月佣金收入 > ¥300
- 约需20-30笔订单/月
- 预计3-6个月达到

---

## 📊 数据统计

### 代码量
- 📝 3768行代码
- 🐍 Python：~1500行
- 📱 小程序：~2200行
- 🔧 配置文件：~100行

### 功能完成度
- ✅ 后端API：100%
- ✅ AI生成：100%
- ✅ 链接替换：90%
- ✅ 前端UI：90%
- 🔄 美团真实返佣：80%
- 🔄 用户系统：0%

---

## 🗺️ Roadmap

### 🎯 Week 1 (当前)
- [x] 后端API完成
- [x] AI攻略生成
- [x] 小程序前端
- [ ] 真机测试
- [ ] 用户反馈

### 🎯 Week 2-4
- [ ] 美团真实返佣对接
- [ ] 用户系统（微信登录）
- [ ] 订单跟踪
- [ ] 返现自动结算

### 🎯 Month 2-3
- [ ] 数据分析（用户画像）
- [ ] 推荐算法优化
- [ ] 增加更多城市数据
- [ ] B端API接口

### 🎯 Month 4-6
- [ ] 小程序上线（正式版）
- [ ] 市场推广
- [ ] 用户增长
- [ ] 盈利验证

---

## 🤝 贡献指南

欢迎贡献代码！

### 贡献流程
1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交改动 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交Pull Request

### 开发规范
- Python：遵循PEP 8
- 小程序：遵循微信官方规范
- 提交信息：使用Emoji前缀（🎉新功能 / 🐛修复 / 📝文档）

---

## 📄 开源协议

本项目采用 [MIT License](LICENSE)

- ✅ 可以商用
- ✅ 可以修改
- ✅ 可以分发
- ⚠️ 需保留版权声明

---

## 📞 联系方式

**项目负责人：** Zero & 老韩

**GitHub：** https://github.com/hanxiao199001/wildtrip

**问题反馈：** [提交Issue](https://github.com/hanxiao199001/wildtrip/issues)

---

## 🙏 致谢

- **DeepSeek** - 提供高性价比AI模型
- **美团联盟** - 提供返佣平台
- **微信小程序** - 提供前端平台
- **开源社区** - 提供技术支持

---

## ⭐ Star History

如果这个项目对你有帮助，请给个Star⭐️！

[![Star History Chart](https://api.star-history.com/svg?repos=hanxiao199001/wildtrip&type=Date)](https://star-history.com/#hanxiao199001/wildtrip&Date)

---

<div align="center">

**🔥 不走寻常路，就走野路子 🔥**

Made with ❤️ by Zero & 老韩  
2026 © WildTrip

</div>
