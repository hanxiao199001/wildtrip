#!/bin/bash
# 通义千问配置向导

echo "========================================"
echo "🚀 野游记 SaaS - 通义千问配置向导"
echo "========================================"
echo ""

# 检查是否已有 .env 文件
if [ -f .env ]; then
    echo "⚠️  检测到已有 .env 文件"
    read -p "是否备份并重新配置？(y/n): " backup
    if [ "$backup" = "y" ]; then
        cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
        echo "✅ 已备份到 .env.backup.$(date +%Y%m%d_%H%M%S)"
    else
        echo "取消配置"
        exit 0
    fi
fi

# 输入 API Key
echo ""
echo "📝 请输入通义千问 API Key："
echo "   (在 https://dashscope.console.aliyun.com/ 获取)"
read -p "API Key: " api_key

if [ -z "$api_key" ]; then
    echo "❌ API Key 不能为空"
    exit 1
fi

# 选择模型
echo ""
echo "🤖 请选择模型："
echo "  1. qwen-turbo  (便宜、快速、适合测试)"
echo "  2. qwen-plus   (推荐、性价比高)"
echo "  3. qwen-max    (最强、最贵)"
read -p "选择 (1/2/3, 默认2): " model_choice

case $model_choice in
    1) model="qwen-turbo" ;;
    3) model="qwen-max" ;;
    *) model="qwen-plus" ;;
esac

# 生成 .env 文件
cat > .env << EOF
# 野游记 AI 配置 (通义千问)
# 生成时间: $(date)

# ============================================
# 通义千问 (Qwen) 配置
# ============================================
AI_API_KEY=$api_key
AI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
AI_MODEL=$model

# ============================================
# 微信公众号配置（后续配置）
# ============================================
# WECHAT_TOKEN=wildtrip_saas_token
# WECHAT_APPID=wx...
# WECHAT_SECRET=...
EOF

echo ""
echo "✅ 配置文件已生成: .env"
echo ""
echo "配置信息："
echo "  API Key: ${api_key:0:20}..."
echo "  Base URL: https://dashscope.aliyuncs.com/compatible-mode/v1"
echo "  Model: $model"
echo ""

# 测试 API
echo "🧪 是否立即测试 API？(y/n)"
read -p "测试: " test_api

if [ "$test_api" = "y" ]; then
    echo ""
    echo "⏳ 加载配置并测试..."
    export $(cat .env | grep -v '^#' | xargs)
    python3 saas/test_qwen_api.py
else
    echo ""
    echo "配置完成！可以手动测试："
    echo "  source .env"
    echo "  python3 saas/test_qwen_api.py"
fi
