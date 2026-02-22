#!/bin/bash
# 更新百度统计ID

if [ -z "$1" ]; then
    echo "用法: ./update_baidu_id.sh <百度统计ID>"
    echo "示例: ./update_baidu_id.sh abc123def456"
    exit 1
fi

BAIDU_ID=$1
SEO_FILE="/root/clawd/backend/services/seo_optimizer.py"

# 备份
cp $SEO_FILE ${SEO_FILE}.bak

# 替换ID
sed -i "s/your_baidu_analytics_id_here/$BAIDU_ID/g" $SEO_FILE

echo "✅ 百度统计ID已更新为: $BAIDU_ID"
echo "📁 原文件已备份为: ${SEO_FILE}.bak"
echo ""
echo "🎯 下一步:"
echo "   1. 重新生成所有页面: cd /root/clawd && python backend/batch_generate_guides.py"
echo "   2. 部署页面到服务器"
echo "   3. 提交sitemap到百度: https://ziyuan.baidu.com"
