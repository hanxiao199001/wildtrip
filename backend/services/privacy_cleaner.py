"""
隐私信息清洗服务
在保存SEO页面前，自动清洗用户的个人信息，防止隐私泄露
"""

import re
from loguru import logger


class PrivacyCleaner:
    """隐私信息清洗器"""
    
    def __init__(self):
        """初始化清洗规则"""
        # 编译正则表达式（提高性能）
        self.patterns = {
            # 手机号：13800138000、+86 138 0013 8000
            'phone': re.compile(r'(?:\+86[\s-]?)?1[3-9]\d{1}[\s-]?\d{4}[\s-]?\d{4}'),
            
            # 身份证号：18位
            'id_card': re.compile(r'\b\d{17}[\dXx]\b'),
            
            # 银行卡号：16-19位
            'bank_card': re.compile(r'\b\d{16,19}\b'),
            
            # 邮箱：xxx@xxx.com
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            
            # 详细地址：XX省XX市XX区XX街道XX号
            'address': re.compile(r'[\u4e00-\u9fa5]+省[\u4e00-\u9fa5]+市[\u4e00-\u9fa5]+区[\u4e00-\u9fa5]+街道?[\u4e00-\u9fa5\d]+号?'),
            
            # 车牌号：京A12345
            'car_plate': re.compile(r'[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领][A-Z][A-HJ-NP-Z0-9]{5}'),
            
            # 护照号：G12345678、E12345678
            'passport': re.compile(r'\b[GE]\d{8}\b'),
            
            # 具体金额：¥1234.56、1234.56元
            'money_detail': re.compile(r'[¥￥]\s?\d{4,}(?:\.\d{1,2})?|(?:\d{4,}(?:\.\d{1,2})?)\s?[元块]'),
            
            # 微信号：wxid_xxx、微信:xxx
            'wechat': re.compile(r'(?:微信[号]?|WeChat|wxid)[：:\s]*[a-zA-Z0-9_-]{5,}'),
            
            # QQ号：5位以上数字
            'qq': re.compile(r'QQ[号]?[：:\s]*\d{5,}'),
        }
        
        logger.info("✅ 隐私清洗器初始化完成")
    
    def clean_query(self, query: str) -> tuple:
        """
        清洗用户查询中的个人信息
        
        Args:
            query: 原始查询（如"我和张三去上海，电话13800138000"）
            
        Returns:
            (cleaned_query, is_sensitive)
            cleaned_query: 清洗后的查询（如"2人去上海"）
            is_sensitive: 是否包含敏感信息
        """
        original = query
        cleaned = query
        found_patterns = []
        
        # 检测并替换各类敏感信息
        for pattern_name, pattern in self.patterns.items():
            matches = pattern.findall(cleaned)
            if matches:
                found_patterns.append(pattern_name)
                
                # 根据类型进行替换
                if pattern_name == 'phone':
                    cleaned = pattern.sub('[手机号已隐藏]', cleaned)
                elif pattern_name == 'email':
                    cleaned = pattern.sub('[邮箱已隐藏]', cleaned)
                elif pattern_name == 'id_card':
                    cleaned = pattern.sub('[身份证已隐藏]', cleaned)
                elif pattern_name == 'bank_card':
                    cleaned = pattern.sub('[银行卡已隐藏]', cleaned)
                elif pattern_name == 'address':
                    cleaned = pattern.sub('[地址已隐藏]', cleaned)
                elif pattern_name == 'car_plate':
                    cleaned = pattern.sub('[车牌已隐藏]', cleaned)
                elif pattern_name == 'passport':
                    cleaned = pattern.sub('[护照已隐藏]', cleaned)
                elif pattern_name == 'money_detail':
                    cleaned = pattern.sub('[金额]', cleaned)
                elif pattern_name == 'wechat':
                    cleaned = pattern.sub('[微信已隐藏]', cleaned)
                elif pattern_name == 'qq':
                    cleaned = pattern.sub('[QQ已隐藏]', cleaned)
        
        # 🔥 清洗可能的姓名（中文2-4字）
        # 只清洗"我和XXX"、"XXX同学"等明显的姓名模式
        name_patterns = [
            (r'我和([\u4e00-\u9fa5]{2,4})', '我和朋友'),
            (r'([\u4e00-\u9fa5]{2,4})同学', '朋友'),
            (r'([\u4e00-\u9fa5]{2,4})老师', '老师'),
            (r'([\u4e00-\u9fa5]{2,4})女士', '女士'),
            (r'([\u4e00-\u9fa5]{2,4})先生', '先生'),
        ]
        
        for pattern, replacement in name_patterns:
            if re.search(pattern, cleaned):
                cleaned = re.sub(pattern, replacement, cleaned)
                found_patterns.append('name')
        
        # 判断是否包含敏感信息
        is_sensitive = len(found_patterns) > 0
        
        if is_sensitive:
            logger.warning(f"⚠️ 检测到敏感信息: {found_patterns} | 原始: {original[:30]}... | 清洗后: {cleaned[:30]}...")
        
        return cleaned, is_sensitive
    
    def clean_content(self, content: str) -> str:
        """
        清洗攻略内容中的个人信息
        
        Args:
            content: 原始内容（Markdown格式）
            
        Returns:
            清洗后的内容
        """
        cleaned = content
        
        # 清洗各类敏感信息
        for pattern_name, pattern in self.patterns.items():
            matches = pattern.findall(cleaned)
            if matches:
                logger.warning(f"⚠️ 内容中发现{pattern_name}: {len(matches)}处")
                
                # 根据类型替换
                if pattern_name == 'phone':
                    cleaned = pattern.sub('***', cleaned)
                elif pattern_name == 'email':
                    cleaned = pattern.sub('***@***.com', cleaned)
                elif pattern_name == 'id_card':
                    cleaned = pattern.sub('***', cleaned)
                elif pattern_name == 'bank_card':
                    cleaned = pattern.sub('***', cleaned)
                elif pattern_name == 'address':
                    # 保留城市，隐藏详细地址
                    cleaned = pattern.sub('[详细地址已隐藏]', cleaned)
                elif pattern_name == 'car_plate':
                    cleaned = pattern.sub('***', cleaned)
                elif pattern_name == 'passport':
                    cleaned = pattern.sub('***', cleaned)
                elif pattern_name == 'money_detail':
                    # 🔥 不清洗！预算金额是攻略核心内容，保留
                    # cleaned = pattern.sub('[预算]', cleaned)
                    pass  # 保持原样
                elif pattern_name == 'wechat':
                    cleaned = pattern.sub('[微信号]', cleaned)
                elif pattern_name == 'qq':
                    cleaned = pattern.sub('[QQ号]', cleaned)
        
        return cleaned
    
    def should_save_to_seo(self, query: str, content: str) -> tuple:
        """
        判断是否应该保存为公开的SEO页面
        
        Args:
            query: 用户查询
            content: 攻略内容
            
        Returns:
            (should_save, reason)
            should_save: 是否保存（True/False）
            reason: 原因说明
        """
        # 清洗query
        cleaned_query, is_query_sensitive = self.clean_query(query)
        
        # 检查content
        has_phone = bool(self.patterns['phone'].search(content))
        has_email = bool(self.patterns['email'].search(content))
        has_id_card = bool(self.patterns['id_card'].search(content))
        
        # 🔥 判断规则：如果包含严重敏感信息，不保存
        if has_id_card:
            return False, "内容包含身份证号，不适合公开"
        
        if has_phone and has_email:
            return False, "内容包含多种联系方式，可能是私人行程"
        
        # 🔥 如果只是轻度敏感（如预算金额），清洗后可以保存
        return True, "清洗后可以公开"


# 单例
_privacy_cleaner_instance = None


def get_privacy_cleaner() -> PrivacyCleaner:
    """获取隐私清洗器实例（单例模式）"""
    global _privacy_cleaner_instance
    
    if _privacy_cleaner_instance is None:
        _privacy_cleaner_instance = PrivacyCleaner()
    
    return _privacy_cleaner_instance


# 示例用法
if __name__ == "__main__":
    cleaner = PrivacyCleaner()
    
    # 测试query清洗
    test_queries = [
        "我和张三去上海3天，电话13800138000",
        "海口亲子游，预算5000元",
        "成都4天，地址：四川省成都市武侯区天府大道123号",
        "杭州周末游",  # 正常查询
    ]
    
    print("=== Query清洗测试 ===")
    for query in test_queries:
        cleaned, is_sensitive = cleaner.clean_query(query)
        print(f"原始: {query}")
        print(f"清洗: {cleaned}")
        print(f"敏感: {is_sensitive}")
        print()
    
    # 测试content清洗
    test_content = """
    # 上海3天游攻略
    
    联系人：张三
    电话：13800138000
    微信：wxid_abc123
    预算：¥5000元
    
    **小杨生煎** ¥15/人
    """
    
    print("=== Content清洗测试 ===")
    print("原始内容:")
    print(test_content)
    print("\n清洗后:")
    print(cleaner.clean_content(test_content))
