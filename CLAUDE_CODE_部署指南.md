# Claude Code 快速部署指南 - 需求澄清功能

## 🎯 任务目标

为野游记小程序添加**需求澄清功能**，通过AI智能提问提升攻略质量。

---

## 📦 需要创建的文件

### 后端（3个文件）

1. **`backend/services/need_clarifier.py`** - 需求澄清服务
2. **`backend/api/clarify.py`** - API接口
3. **修改 `backend/app.py`** - 注册新蓝图

### 前端（4个新文件 + 2个修改）

1. **`miniprogram/pages/clarify/clarify.wxml`**
2. **`miniprogram/pages/clarify/clarify.wxss`**
3. **`miniprogram/pages/clarify/clarify.js`**
4. **`miniprogram/pages/clarify/clarify.json`**
5. **修改 `miniprogram/pages/index/index.js`**
6. **修改 `miniprogram/utils/api.js`**

---

## ⚡ 快速实施步骤

### Phase 1: 后端实现（复制粘贴）

#### 步骤1.1: 创建 need_clarifier.py

位置: `backend/services/need_clarifier.py`

<详细代码见 `/tmp/clarify_page_guide.md` 中的后端部分>

关键点：
- 问题模板库（预算、人数、住宿、美食）
- 智能检测逻辑（检测query中是否包含关键信息）
- 查询增强（根据用户回答补充信息）

#### 步骤1.2: 创建 clarify.py API

位置: `backend/api/clarify.py`

关键点：
- `/api/analyze-need` - 分析需求返回问题
- `/api/generate-with-answers` - 带答案生成攻略

#### 步骤1.3: 注册蓝图

修改 `backend/app.py`，添加：

```python
from api.clarify import clarify_bp

app.register_blueprint(clarify_bp, url_prefix='/api')
```

---

### Phase 2: 前端实现（复制粘贴）

#### 步骤2.1: 创建澄清页面

在 `miniprogram/pages/` 下创建 `clarify` 文件夹，添加4个文件。

**完整代码见:** `/tmp/clarify_page_guide.md`

#### 步骤2.2: 修改首页跳转

修改 `miniprogram/pages/index/index.js` 的 `onGenerate` 方法：

```javascript
onGenerate() {
  const { query } = this.data
  
  if (!query.trim()) {
    wx.showToast({
      title: '请输入您的需求',
      icon: 'none'
    })
    return
  }

  // 🆕 跳转到需求澄清页
  wx.navigateTo({
    url: `/pages/clarify/clarify?query=${encodeURIComponent(query)}`
  })
}
```

#### 步骤2.3: 添加API方法

修改 `miniprogram/utils/api.js`，添加：

```javascript
/**
 * 分析需求
 */
function analyzeNeed(query) {
  return request('/analyze-need', { query }, 'POST')
}

/**
 * 带答案生成攻略
 */
function generateWithAnswers(originalQuery, answers) {
  return request('/generate-with-answers', {
    original_query: originalQuery,
    answers: answers
  }, 'POST')
}

module.exports = {
  // ... 原有方法
  analyzeNeed,
  generateWithAnswers
}
```

#### 步骤2.4: 注册页面

修改 `miniprogram/app.json`，添加：

```json
{
  "pages": [
    "pages/index/index",
    "pages/clarify/clarify",  // 🆕 添加这一行
    "pages/generate/generate",
    "pages/result/result",
    "pages/cashback/cashback",
    "pages/webview/webview"
  ]
}
```

---

## ✅ 验证步骤

### 1. 后端测试

```bash
# 启动后端
cd backend
python app.py

# 测试API（新开终端）
curl -X POST http://localhost:5000/api/analyze-need \
  -H "Content-Type: application/json" \
  -d '{"query":"海口3天亲子游"}'

# 预期返回：
{
  "original_query": "海口3天亲子游",
  "questions": [
    {
      "id": "budget",
      "question": "您的预算范围是？",
      "options": [...]
    },
    ...
  ]
}
```

### 2. 前端测试

1. 打开微信开发者工具
2. 点击"编译"
3. 在首页输入："海口3天亲子游"
4. 点击"生成攻略"按钮
5. 应该跳转到需求澄清页
6. 查看问题是否正常显示
7. 选择几个选项
8. 点击"确认"按钮
9. 验证是否跳转到生成页

---

## 🎨 界面效果预览

```
┌──────────────────────────────┐
│ ← 完善需求                    │
├──────────────────────────────┤
│                               │
│ ┌────────────────────────┐  │
│ │ 📝 您的需求             │  │
│ │ "海口3天亲子游"         │  │
│ └────────────────────────┘  │
│                               │
│ ┌────────────────────────┐  │
│ │ 🤖 为了生成更精准的     │  │
│ │    攻略，请帮我完善...  │  │
│ └────────────────────────┘  │
│                               │
│ ┌────────────────────────┐  │
│ │ Q1 您的预算范围是？[必填]│ │
│ │                         │  │
│ │ ┌────────────────────┐ │  │
│ │ │ 💰 经济实惠         │ │  │
│ │ │ ¥1000-2000         │ │  │
│ │ └────────────────────┘ │  │
│ │                         │  │
│ │ ┌────────────────────┐ │  │ ← 选中状态
│ │ │ 💎 舒适出游 ✓       │ │  │   (绿色边框)
│ │ │ ¥2000-5000         │ │  │
│ │ └────────────────────┘ │  │
│ │                         │  │
│ │ ┌────────────────────┐ │  │
│ │ │ 👑 品质优先         │ │  │
│ │ │ ¥5000+             │ │  │
│ │ └────────────────────┘ │  │
│ └────────────────────────┘  │
│                               │
│ ┌────────────────────────┐  │
│ │ Q2 出行人数是？[必填]   │  │
│ │ ...                     │  │
│ └────────────────────────┘  │
│                               │
├──────────────────────────────┤
│ [跳过，直接生成] [确认 (2/3)] │
└──────────────────────────────┘
```

---

## 🔑 关键实现要点

### 1. 智能提问逻辑

```python
def analyze_need(self, query: str) -> Dict[str, Any]:
    """分析用户需求，返回需要澄清的问题"""
    questions = []
    
    # 检测预算
    if not self._has_budget_info(query):
        questions.append(self.QUESTION_TEMPLATES["budget"])
    
    # 检测人数
    if not self._has_people_count(query):
        questions.append(self.QUESTION_TEMPLATES["people_count"])
    
    # 最多5个问题
    return {
        "original_query": query,
        "questions": questions[:5]
    }
```

### 2. 查询增强

```python
def enhance_query(self, original_query: str, answers: Dict) -> str:
    """根据用户回答增强原始查询"""
    enhanced_parts = [original_query]
    
    if "budget" in answers:
        enhanced_parts.append("预算中等，人均2000-3000元/天")
    
    if "people_count" in answers:
        enhanced_parts.append(f"出行人数{answers['people_count']}")
    
    return "，".join(filter(None, enhanced_parts))
```

### 3. 选项状态管理

```javascript
onSelectOption(e) {
  const { questionId, value } = e.currentTarget.dataset
  const { selectedAnswers } = this.data
  
  selectedAnswers[questionId] = value
  this.setData({ selectedAnswers })
  this.updateAnswerStatus()
}

updateAnswerStatus() {
  const { questions, selectedAnswers } = this.data
  
  // 计算已回答的必填题
  const answeredRequired = questions.filter(q => 
    q.required && selectedAnswers[q.id]
  ).length
  
  // 是否可以确认
  const canConfirm = answeredRequired === this.data.requiredCount
  
  this.setData({ canConfirm })
}
```

---

## 📚 参考文档

1. **完整设计文档:** `/root/clawd/需求澄清功能设计文档.md`
2. **详细代码:** `/tmp/clarify_page_guide.md`
3. **UI设计规范:** 参考现有页面风格

---

## 🚨 注意事项

### 1. 性能要求

- API响应时间 < 500ms
- 问题数量 ≤ 5个
- 必填题 ≤ 3个

### 2. 用户体验

- ✅ 必须提供"跳过"选项
- ✅ 进度提示清晰（已回答x/总数y）
- ✅ 选中状态明显（颜色+边框+图标）

### 3. 降级方案

- API失败时，询问用户是否直接生成
- 超时时（>3秒），自动跳过

---

## ✅ 完成检查清单

**后端:**
- [ ] `need_clarifier.py` 创建完成
- [ ] `clarify.py` 创建完成
- [ ] `app.py` 注册蓝图
- [ ] API测试通过

**前端:**
- [ ] `clarify` 页面4个文件创建完成
- [ ] `index.js` 修改完成
- [ ] `api.js` 添加新方法
- [ ] `app.json` 注册页面
- [ ] 编译通过
- [ ] 功能测试通过

**测试:**
- [ ] 输入 → 跳转澄清页
- [ ] 问题正常显示
- [ ] 选项可点击
- [ ] 选中状态正确
- [ ] 跳过功能正常
- [ ] 确认后正常生成

---

## 🎯 预期耗时

- **后端实现:** 30分钟
- **前端实现:** 40分钟
- **测试验证:** 20分钟
- **总计:** 约1.5小时

---

**准备好了吗？开始实施吧！** 🚀

有任何问题，参考详细文档或联系我！
