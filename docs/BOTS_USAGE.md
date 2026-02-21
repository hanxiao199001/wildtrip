# 三机器人内容生产流水线使用指南

> 自动化内容生产：从选题 → 生成 → 发布

---

## 🤖 三个机器人

### **1. 选题机器人** (Topic Hunter)
**功能**：从真实用户问题中挖掘选题

**数据来源**：
- 百度搜索建议 API（真实搜索词）
- 模板生成（保底方案）

**输出**：20-30 个高质量选题（JSON 格式）

**时间**：20 分钟

---

### **2. 内容生产机器人** (Content Generator)
**功能**：生成攻略并进行质检

**质检标准**（4 项）：
1. FAQ 包含具体数字（价格、距离、时间等）
2. FAQ 包含地名
3. Affiliate 链接正确嵌入
4. 标题是答案式的（GEO 友好）

**自动修复**：
- FAQ 缺数字/地名 → 补充示例 FAQ
- 缺 affiliate 链接 → 添加默认链接占位

**输出**：符合 GEO 标准的完整攻略

**时间**：1 小时/篇

---

### **3. 发布机器人** (Publisher)
**功能**：保存静态页、更新sitemap、验证访问

**执行步骤**：
1. 调用 `seo_service.save_guide()` 保存 HTML
2. 更新 `web/sitemap.xml`
3. 验证页面可访问（HTTP HEAD 请求）

**输出**：已发布的可访问页面

**时间**：20 分钟

---

## 🎛️ 流水线编排器 (Orchestrator)

协调三个机器人按顺序执行。

### **使用方法**

#### **1. 完整流水线**（生产环境）

```bash
cd /root/clawd/wildtrip-existing/backend

# 生成 10 篇
python3 bots/orchestrator.py --count 10

# 生成 30 篇（选题时限 30 分钟）
python3 bots/orchestrator.py --count 30 --topic-time 30
```

#### **2. 使用现有选题**（跳过选题步骤）

```bash
# 先查看已有选题
ls data/topics/

# 使用现有选题文件
python3 bots/orchestrator.py \\
  --skip-topics \\
  --topics-file data/topics/topics_2026-02-21.json \\
  --count 20
```

#### **3. 分步调试模式**（开发/测试）

```bash
python3 bots/orchestrator.py --mode step --count 5
```

每一步会暂停等待你按 Enter 确认。

---

## 📊 执行报告

每次运行都会生成报告：

```bash
cat data/production/production_report_20260221_111530.json
```

**报告内容**：
```json
{
  "start_time": "2026-02-21T11:15:30",
  "end_time": "2026-02-21T13:20:45",
  "total_time_minutes": 125.3,
  "topics_count": 30,
  "generated_count": 28,
  "published_count": 27,
  "generation_results": [...],
  "publish_results": [...]
}
```

---

## 🔧 单独运行某个机器人

### **只运行选题机器人**

```python
from bots.topic_hunter import TopicHunterBot

bot = TopicHunterBot()
topics = bot.hunt_topics(max_topics=30, time_limit_minutes=20)

print(f"选题数量: {len(topics)}")
for topic in topics[:5]:
    print(f"- {topic['title']} (分数: {topic['score']:.2f})")
```

### **只运行内容生产机器人**

```python
from bots.content_generator import ContentGeneratorBot

bot = ContentGeneratorBot()
content, qa_report = bot.generate_with_qa("海口周末带7岁男孩")

print(f"质检通过: {qa_report['passed']}")
print(f"质检分数: {qa_report['score']:.2f}")
print(f"问题: {qa_report['issues']}")
```

### **只运行发布机器人**

```python
from bots.publisher import PublisherBot

bot = PublisherBot()
result = bot.publish(
    topic="海口周末带7岁男孩",
    content=content,
    stats={'word_count': 3000, 'hotels_count': 2, 'restaurants_count': 3}
)

print(f"发布成功: {result['success']}")
print(f"URL: {result['url']}")
```

---

## 📝 选题来源配置

编辑 `backend/bots/topic_hunter.py`：

```python
# 种子关键词（城市）
self.seed_cities = [
    '北京', '上海', '成都', '重庆', '杭州', '西安',
    # 添加更多城市...
]

# 人群关键词
self.crowd_keywords = [
    '带娃', '亲子', '带孩子', '情侣', '闺蜜',
    # 添加更多人群...
]

# 时间关键词
self.time_keywords = [
    '周末', '3天', '春节', '暑假',
    # 添加更多时间...
]
```

---

## ⚙️ 质检标准调整

编辑 `backend/bots/content_generator.py`：

```python
self.quality_checks = {
    'faq_has_numbers': {
        'name': 'FAQ包含具体数字',
        'weight': 0.3,
        'required': True  # 改为 False 可降低要求
    },
    # 添加自定义检查...
}
```

---

## 🚀 批量生成 1000+ 页面

**策略**：分批次生成，避免 API 限流

```bash
# 第一批：100 篇（约 2-3 小时）
python3 bots/orchestrator.py --count 100

# 等待 1 小时后继续
sleep 3600

# 第二批：100 篇
python3 bots/orchestrator.py --count 100 --skip-topics --topics-file data/topics/topics_latest.json

# ...重复 10 次 → 1000 篇
```

**自动化脚本**：

```bash
#!/bin/bash
# 批量生成 1000 篇

for i in {1..10}; do
  echo "🚀 第 $i 批（100 篇）"
  
  python3 backend/bots/orchestrator.py --count 100
  
  if [ $i -lt 10 ]; then
    echo "😴 休息 1 小时..."
    sleep 3600
  fi
done

echo "✅ 1000 篇全部生成完成"
```

---

## 📊 监控和日志

查看实时日志：

```bash
tail -f logs/wildtrip.log
```

查看今日生成统计：

```bash
cd data/production
ls -lh production_report_$(date +%Y%m%d)*.json
```

---

## ⚠️ 注意事项

### **1. API 限流**
- 通义千问：每分钟 60 次请求
- 如果超限，自动使用 Mock 数据

### **2. 隐私保护**
- 所有内容经过 `privacy_cleaner` 清洗
- 敏感词（手机号、姓名）会被自动过滤

### **3. 质检不通过**
- 第一次自动修复
- 如果仍不通过，会跳过该选题

### **4. 存储空间**
- 每篇攻略约 30KB
- 1000 篇 ≈ 30MB
- 确保有足够磁盘空间

---

## 🐛 常见问题

### **Q1: 选题质量不高？**
**A**: 调整 `topic_hunter.py` 的评分规则：

```python
def _score_and_rank(self, topics):
    # 提高"包含具体年龄"的权重
    if re.search(r'\d+岁', title):
        score += 0.3  # 从 0.2 改为 0.3
```

### **Q2: 生成内容质检总是不通过？**
**A**: 降低质检标准或改进 AI prompt

```python
# 降低通过分数
passed = score >= 0.7  # 从 0.8 改为 0.7
```

### **Q3: 发布后页面无法访问？**
**A**: 检查服务器配置和文件权限

```bash
# 检查文件是否生成
ls -lh /root/clawd/wildtrip/web/guides/

# 检查权限
chmod 644 /root/clawd/wildtrip/web/guides/*.html
```

---

## 📚 相关文档

- [GEO 优化实施文档](./GEO_OPTIMIZATION.md)
- [多智能体架构](./multi-agent-architecture.md)
- [SEO 服务使用指南](./seo-service-guide.md)

---

*最后更新：2026-02-21*
