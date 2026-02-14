"""
野游记 - 需求澄清API
分析用户需求 → 返回选择题 → 增强查询后生成攻略
"""

from flask import Blueprint, jsonify, request
from loguru import logger
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.need_clarifier import NeedClarifier

# 创建Blueprint
clarify_bp = Blueprint('clarify', __name__)

# 初始化服务
clarifier = NeedClarifier()


@clarify_bp.route('/analyze-need', methods=['POST'])
def analyze_need():
    """
    分析用户需求，返回澄清问题

    请求体:
    {
        "query": "海口3天亲子游"
    }

    响应:
    {
        "original_query": "海口3天亲子游",
        "detected": {"destination": "海口", "days": 3, ...},
        "questions": [...],
        "need_clarify": true
    }
    """
    data = request.json
    query = data.get('query', '').strip()

    if not query:
        return jsonify({'error': '缺少query参数'}), 400

    try:
        result = clarifier.analyze_need(query)
        logger.info(f"📋 需求分析: '{query}' → 检测到{len(result.get('detected', {}))}项信息，需要澄清{len(result.get('questions', []))}个问题")
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"❌ 需求分析失败: {e}")
        return jsonify({'error': str(e)}), 500


@clarify_bp.route('/enhance-query', methods=['POST'])
def enhance_query():
    """
    根据用户回答增强查询

    请求体:
    {
        "original_query": "海口3天亲子游",
        "answers": {
            "budget": "budget_mid",
            "people": "family",
            "accommodation": "comfort_hotel"
        }
    }

    响应:
    {
        "enhanced_query": "海口3天亲子游，预算中等，追求舒适..."
    }
    """
    data = request.json
    original_query = data.get('original_query', '').strip()
    answers = data.get('answers', {})

    if not original_query:
        return jsonify({'error': '缺少original_query参数'}), 400

    try:
        enhanced = clarifier.enhance_query(original_query, answers)
        logger.info(f"✨ 查询增强: '{original_query}' → '{enhanced[:80]}...'")
        return jsonify({
            'original_query': original_query,
            'enhanced_query': enhanced,
            'answers': answers
        }), 200
    except Exception as e:
        logger.error(f"❌ 查询增强失败: {e}")
        return jsonify({'error': str(e)}), 500
