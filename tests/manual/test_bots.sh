#!/bin/bash
# 测试三机器人流水线

cd /root/clawd/wildtrip-existing/backend

echo "🤖 野游记三机器人流水线测试"
echo "================================"
echo ""

# 测试1: 选题机器人
echo "📋 测试1: 选题机器人"
python3 -c "
from bots.topic_hunter import TopicHunterBot
bot = TopicHunterBot()
topics = bot.hunt_topics(max_topics=5, time_limit_minutes=1)
print(f'✅ 选题数量: {len(topics)}')
for i, t in enumerate(topics[:3], 1):
    print(f'  {i}. {t[\"title\"]}')
"

echo ""
echo "================================"
echo ""

# 测试2: 内容生产机器人（Mock模式，快速）
echo "📝 测试2: 内容生产机器人"
python3 -c "
from bots.content_generator import ContentGeneratorBot
bot = ContentGeneratorBot()

# 使用 Mock 数据快速测试
print('ℹ️ 使用 Mock 数据快速测试质检功能')

# 模拟内容
mock_content = '''
# 海口周末带7岁男孩攻略

## 住宿推荐
### 1. 海口柚庐民宿
**价格**: ¥350/晚
[美团预订](meituan://...)

## 💬 常见问题
### 海口周末适合吗？
海口周末气温约20-25℃，距离市区约15公里，适合带孩子。预算约¥2000。
'''

qa_report = bot._quality_check('海口周末带7岁男孩', mock_content, {})
print(f'✅ 质检分数: {qa_report[\"score\"]:.2f}')
print(f'✅ 是否通过: {qa_report[\"passed\"]}')
for check_name, result in qa_report['checks'].items():
    status = '✅' if result['passed'] else '❌'
    print(f'  {status} {check_name}')
"

echo ""
echo "================================"
echo ""

# 测试3: 发布机器人
echo "📤 测试3: 发布机器人"
python3 -c "
from bots.publisher import PublisherBot
bot = PublisherBot()

result = bot.publish(
    topic='测试攻略_$(date +%s)',
    content='# 测试内容',
    stats={'word_count': 100, 'hotels_count': 1, 'restaurants_count': 1}
)

print(f'✅ 发布成功: {result[\"success\"]}')
if result.get('url'):
    print(f'✅ URL: {result[\"url\"]}')
"

echo ""
echo "================================"
echo "✅ 所有测试完成"
