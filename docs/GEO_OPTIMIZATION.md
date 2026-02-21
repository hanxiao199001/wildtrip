# GEO（生成式引擎优化）实施文档

> 让 AI 搜索引擎（Kimi、豆包、千问、ChatGPT Search）能够抓取和引用野游记的攻略内容

## 📋 目标

传统 SEO 优化百度/Google，但 AI 搜索引擎需要更结构化的内容：
- **FAQ 模块**：直接回答用户问题
- **Schema.org 结构化数据**：让 AI 理解实体信息（酒店、餐厅）
- **答案式标题**：从"XX攻略"改为"{问题}：{答案}"

---

## ✅ 已完成功能

### 1️⃣ FAQ 模块 + JSON-LD

**位置**：每个攻略页面底部

**生成逻辑**：`backend/services/itinerary_generator.py`
- 从攻略内容中提取 5-8 个常见问题
- 根据 query 自动生成答案（包含具体数字、地名、价格）

**示例问题**：
- "海口二月份带7岁孩子去哪个海滩人少？"
- "海口3天亲子游人均预算多少？"
- "海口住哪里方便？推荐XX民宿吗？"

**答案要求**：
- 必须包含具体实体信息（数字、地名、价格）
- 避免泛泛而谈（"具体情况具体分析"❌）

**JSON-LD 结构化数据**：
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "海口二月份带7岁孩子去哪个海滩人少？",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "西海岸后海角石滩，从市区开车约40分钟，退潮时段（约15:30-17:30）水深仅20-50cm，几乎无游客，适合学龄儿童赶海。"
      }
    }
  ]
}
```

---

### 2️⃣ Schema.org 结构化标记

**位置**：酒店和餐厅卡片

**实现方式**：HTML5 Microdata（`itemscope` + `itemprop`）

#### 酒店标记示例
```html
<div itemscope itemtype="https://schema.org/Hotel">
  <span itemprop="name">海口柚庐民宿</span>
  <span itemprop="priceRange">¥350/晚</span>
  <div itemprop="address" itemscope itemtype="https://schema.org/PostalAddress">
    <meta itemprop="addressLocality" content="海口">
    <span itemprop="streetAddress">西海岸观海台1号</span>
  </div>
  <span itemprop="starRating" itemscope itemtype="https://schema.org/Rating">
    <meta itemprop="ratingValue" content="4.8">
  </span>
</div>
```

#### 餐厅标记示例
```html
<div itemscope itemtype="https://schema.org/Restaurant">
  <span itemprop="name">海南粉老店</span>
  <span itemprop="priceRange">¥¥</span>
  <span itemprop="servesCuisine">海南粉</span>
  <span itemprop="servesCuisine">清补凉</span>
</div>
```

**代码位置**：
- `backend/services/itinerary_generator.py` → `HotelExtractor.render_hotel_card()`
- `backend/services/affiliate_manager.py` → `_render_restaurant_card()`

---

### 3️⃣ 答案式标题

**改进前**：
```
海口周末带7岁男孩 - 野游记AI攻略 | 不走寻常路的旅行指南
```

**改进后**：
```
海口周末带7岁男孩：恒温泳池民宿+野海滩赶海 - 野游记
```

**生成规则**：
- 如果 query 包含城市+天数+人群 → 生成答案式标题
- 否则 → 降级为通用格式

**代码位置**：`backend/services/seo_service.py`
- `_generate_answer_style_title()` 生成标题
- `_extract_title_highlights()` 从内容提取核心亮点

**提取优先级**：
1. 酒店特色（恒温泳池、民宿风格）
2. 核心活动（赶海、博物馆）
3. 美食特色
4. 时间特色（48小时方案）

---

## 🧪 测试

### 快速测试
```bash
cd /root/clawd/wildtrip-existing
python3 test_geo_optimization.py
```

### 完整测试（真实数据）
```bash
python3 test_geo_with_real_data.py
```

**检查项**：
- ✅ FAQ 模块是否生成
- ✅ FAQ JSON-LD 是否符合 Schema.org 规范
- ✅ 酒店/餐厅是否有 `itemtype="https://schema.org/Hotel"`
- ✅ 标题是否为答案式（包含"："）

---

## 🚀 批量重新生成现有页面

如果需要给现有的 100+ SEO 页面添加 GEO 优化：

```bash
cd /root/clawd/wildtrip-existing
node scripts/seo-batch-regenerate.js
```

**注意**：需要先创建 `seo-batch-regenerate.js` 脚本（调用 AI 引擎重新生成内容）

---

## 📊 效果评估

### 短期指标（1-2周）
- **Google Search Console**：检查 FAQ rich snippets 是否出现
- **百度站长平台**：结构化数据验证

### 中期指标（1个月）
- **AI 搜索引擎引用率**：
  - 在 Kimi、豆包、千问中搜索"海口周末亲子游"
  - 检查是否引用野游记的 FAQ 答案

### 长期指标（3个月）
- 来自 AI 搜索引擎的流量占比
- FAQ 页面的 CTR（点击率）

---

## ⚙️ 配置说明

### FAQ 问题数量
默认生成 6-8 个问题，可在 `itinerary_generator.py` 中调整：

```python
def _generate_faq_section(self, ...):
    faqs = self._extract_faqs_from_content(query, content, city)
    return faqs[:8]  # 👈 修改这里
```

### 答案式标题开关
如果不想使用答案式标题，可以在 `seo_service.py` 中禁用：

```python
def generate_html(self, query, content, stats):
    # seo_title = self._generate_answer_style_title(query, content, city)  # 👈 注释掉
    seo_title = None  # 使用默认标题
```

---

## 🐛 常见问题

### Q1: FAQ 问题生成得不准确？
**A**: 调整 `_extract_faqs_from_content()` 中的正则匹配规则，或增加模板问题。

### Q2: 酒店/餐厅没有 Schema.org 标记？
**A**: 检查攻略内容格式是否符合 `HotelExtractor` 的正则匹配要求：
```markdown
### 1. 酒店名
**价格**: ¥350/晚
⭐ 4.8
**位置**: XX区XX路
```

### Q3: 答案式标题提取的亮点不准？
**A**: 在 `_extract_title_highlights()` 中增加正则模式：
```python
activity_patterns = [
    r'(赶海|抓螃蟹)',
    r'(博物馆|科技馆)',
    r'(你的新活动)',  # 👈 添加新模式
]
```

---

## 📚 参考资料

- [Schema.org FAQPage](https://schema.org/FAQPage)
- [Schema.org Hotel](https://schema.org/Hotel)
- [Schema.org Restaurant](https://schema.org/Restaurant)
- [Google Search Gallery - FAQ](https://developers.google.com/search/docs/appearance/structured-data/faqpage)

---

## 🔜 下一步优化

1. **BreadcrumbList 结构化数据**：城市 → 天数 → 人群 导航路径
2. **Review 结构化数据**：用户评价（如果有）
3. **HowTo 结构化数据**：行程步骤（Day 1 → Day 2 → ...）
4. **动态 FAQ 更新**：根据用户真实搜索问题自动补充 FAQ

---

*最后更新：2026-02-21*
