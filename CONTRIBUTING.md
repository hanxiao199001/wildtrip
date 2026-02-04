# 🤝 贡献指南

感谢你对野游记（WildTrip）的关注！

我们欢迎任何形式的贡献：代码、文档、Bug反馈、功能建议。

---

## 📋 贡献方式

### 1. 报告Bug

如果你发现了Bug，请：

1. 在 [Issues](https://github.com/hanxiao199001/wildtrip/issues) 中搜索，确认没有重复
2. 创建新Issue，包含：
   - **Bug描述** - 简洁明了
   - **复现步骤** - 1、2、3...
   - **预期行为** - 应该怎样
   - **实际行为** - 实际怎样
   - **环境信息** - OS、Python版本、微信版本等

### 2. 提出功能建议

有好的想法？

1. 创建Feature Request Issue
2. 描述：
   - **问题** - 现在有什么痛点
   - **方案** - 你的建议
   - **替代方案** - 还有其他方法吗
   - **优先级** - 紧急/重要/一般

### 3. 提交代码

#### 前置要求

- ✅ Python 3.10+
- ✅ Git基础
- ✅ 了解Flask或微信小程序开发

#### 开发流程

**1. Fork仓库**
```bash
# 点击GitHub上的Fork按钮
# 克隆你Fork的仓库
git clone https://github.com/你的用户名/wildtrip.git
cd wildtrip
```

**2. 创建分支**
```bash
# 从main创建功能分支
git checkout -b feature/amazing-feature

# 或者修复bug
git checkout -b fix/bug-description
```

**3. 开发**
```bash
# 配置开发环境
cd backend
cp .env.example .env
# 填入你的API Key

# 安装依赖
pip install -r requirements.txt

# 开始开发...
```

**4. 测试**
```bash
# 运行服务
python3 app.py

# 测试API
curl http://localhost:5000/api/task/test
```

**5. 提交**
```bash
# 添加改动
git add .

# 提交（使用有意义的消息）
git commit -m "✨ 添加XXX功能"

# 推送到你的Fork
git push origin feature/amazing-feature
```

**6. 创建Pull Request**
1. 访问你的Fork仓库
2. 点击"Pull Request"
3. 选择 `base: main` ← `compare: feature/amazing-feature`
4. 填写PR描述
5. 提交

---

## 📝 代码规范

### Python

遵循 [PEP 8](https://pep8.org/)

```python
# ✅ 好的命名
def generate_itinerary(query, mode='full'):
    """生成旅游攻略"""
    pass

# ❌ 不好的命名
def gen(q, m='f'):
    pass
```

**风格要求：**
- 缩进：4个空格
- 行宽：120字符
- 注释：中文OK
- 文档字符串：必须有

### JavaScript（小程序）

遵循 [Standard JS](https://standardjs.com/)

```javascript
// ✅ 好的写法
async function generateItinerary(query) {
  const result = await api.generate({ query })
  return result
}

// ❌ 不好的写法
function gen(q){return api.generate({query:q})}
```

**风格要求：**
- 缩进：2个空格
- 分号：可选（但要统一）
- 注释：中文OK

---

## 🎯 Commit规范

使用Emoji + 类型 + 描述

### Emoji类型

| Emoji | 类型 | 示例 |
|-------|------|------|
| ✨ | 新功能 | `✨ 添加酒店推荐功能` |
| 🐛 | Bug修复 | `🐛 修复链接提取错误` |
| 📝 | 文档 | `📝 更新README` |
| 🎨 | 样式/格式 | `🎨 优化小程序UI` |
| ⚡️ | 性能 | `⚡️ 优化AI生成速度` |
| 🔧 | 配置 | `🔧 添加.env.example` |
| ♻️ | 重构 | `♻️ 重构链接生成逻辑` |
| 🚀 | 部署 | `🚀 配置GitHub Actions` |

### 示例

```bash
# ✅ 好的commit
git commit -m "✨ 添加美食推荐模式"
git commit -m "🐛 修复DeepSeek API超时问题"
git commit -m "📝 完善CONTRIBUTING文档"

# ❌ 不好的commit
git commit -m "update"
git commit -m "fix bug"
git commit -m "改了点东西"
```

---

## 🧪 测试要求

目前测试框架还在完善，但请确保：

**手动测试：**
1. ✅ 代码无语法错误
2. ✅ API能正常响应
3. ✅ 小程序能正常使用
4. ✅ 没有破坏现有功能

**后续计划：**
- 单元测试（pytest）
- 集成测试
- E2E测试

---

## 📚 开发资源

### 文档

- [快速开始](docs/快速开始.md)
- [前端开发指南](FRONTEND_DEV.md)
- [API文档](docs/)

### 技术栈

- **后端**: [Flask文档](https://flask.palletsprojects.com/)
- **AI**: [DeepSeek文档](https://platform.deepseek.com/docs)
- **前端**: [微信小程序文档](https://developers.weixin.qq.com/miniprogram/dev/framework/)

### 工具

- **Python格式化**: `black`
- **JS格式化**: `prettier`
- **Git工具**: `git-flow`

---

## 💬 交流方式

- **GitHub Issues** - 问题讨论
- **Pull Request** - 代码审查
- **Discussions** - 功能讨论

---

## 🎖️ 贡献者

感谢所有贡献者！

<!-- ALL-CONTRIBUTORS-LIST:START -->
<!-- ALL-CONTRIBUTORS-LIST:END -->

---

## ⚖️ 行为准则

请遵守以下准则：

1. **尊重他人** - 友善、包容、专业
2. **建设性反馈** - 提出问题时带上建议
3. **开放心态** - 接受不同观点
4. **遵守协议** - MIT License

---

## 🙏 致谢

感谢你花时间阅读本指南！

期待你的贡献 🎉

---

*Questions? 提 [Issue](https://github.com/hanxiao199001/wildtrip/issues) 或直接PR！*

**🔥 不走寻常路，就走野路子 🔥**
