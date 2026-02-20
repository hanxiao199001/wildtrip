"""
智能比价监控服务
对接 pricing-system 或 API
"""

import requests
from typing import Optional, List
from loguru import logger
from core.trip_state import PricingInsight


class PricingMonitor:
    """
    价格监控器
    
    集成 pricing-system 或调用第三方 API
    """
    
    def __init__(self):
        # pricing-system 的 API 地址（如果本地部署）
        self.pricing_api = "http://localhost:5001"  # 示例
        
        # 是否启用真实比价（默认关闭，使用 Mock）
        self.enable_real_pricing = False
    
    def check_price(
        self,
        hotel_name: str,
        destination: str,
        check_in: Optional[str] = None
    ) -> Optional[PricingInsight]:
        """
        检查酒店价格
        
        Args:
            hotel_name: 酒店名称
            destination: 目的地
            check_in: 入住日期 (YYYY-MM-DD)
            
        Returns:
            价格洞察，如果没有数据则返回 None
        """
        if self.enable_real_pricing:
            return self._check_price_real(hotel_name, destination, check_in)
        else:
            return self._check_price_mock(hotel_name, destination)
    
    def _check_price_real(
        self,
        hotel_name: str,
        destination: str,
        check_in: Optional[str] = None
    ) -> Optional[PricingInsight]:
        """
        真实比价（调用 pricing-system API）
        
        TODO: 集成 pricing-system 的实际 API
        """
        try:
            # 示例 API 调用
            response = requests.get(
                f"{self.pricing_api}/api/compare",
                params={
                    'hotel': hotel_name,
                    'city': destination,
                    'date': check_in
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # 解析返回数据
                return PricingInsight(
                    hotel_name=hotel_name,
                    platform=data.get('best_platform', 'meituan'),
                    current_price=data.get('best_price', 0),
                    trend=data.get('trend', 'stable'),
                    suggestion=data.get('suggestion', '价格稳定')
                )
        
        except Exception as e:
            logger.warning(f"⚠️ 真实比价失败: {e}")
            return None
    
    def _check_price_mock(
        self,
        hotel_name: str,
        destination: str
    ) -> Optional[PricingInsight]:
        """
        Mock 比价数据（用于测试）
        
        根据酒店名称生成模拟的价格趋势
        """
        # 简单的 Mock 逻辑
        import hashlib
        
        # 用酒店名称生成一个"伪随机"的价格和趋势
        hash_val = int(hashlib.md5(hotel_name.encode()).hexdigest()[:8], 16)
        
        price_base = (hash_val % 500) + 300  # 300-800 区间
        
        # 根据 hash 决定趋势
        trend_options = ['rising', 'falling', 'stable']
        trend = trend_options[hash_val % 3]
        
        # 根据趋势生成建议
        if trend == 'rising':
            suggestion = "价格正在上涨，建议尽快预订"
            platform = "携程"
            price = price_base
        elif trend == 'falling':
            suggestion = "价格下降中，可再观察1-2天"
            platform = "美团"
            price = price_base - 50
        else:
            suggestion = "价格稳定，可随时预订"
            platform = "飞猪"
            price = price_base
        
        logger.info(f"💰 Mock 比价: {hotel_name} - {platform} ¥{price} ({trend})")
        
        return PricingInsight(
            hotel_name=hotel_name,
            platform=platform,
            current_price=price,
            trend=trend,
            suggestion=suggestion
        )
    
    def get_multi_platform_prices(
        self,
        hotel_name: str,
        destination: str
    ) -> List[dict]:
        """
        获取多平台价格对比
        
        Returns:
            [
                {'platform': 'meituan', 'price': 680},
                {'platform': 'ctrip', 'price': 720},
                {'platform': 'feizhu', 'price': 690}
            ]
        """
        # Mock 数据
        import hashlib
        hash_val = int(hashlib.md5(hotel_name.encode()).hexdigest()[:8], 16)
        
        base_price = (hash_val % 500) + 300
        
        return [
            {'platform': '美团', 'price': base_price - 20},
            {'platform': '携程', 'price': base_price},
            {'platform': '飞猪', 'price': base_price + 10}
        ]


# ========== 便捷函数 ==========

def compare_hotel_prices(hotel_name: str, destination: str) -> str:
    """
    生成酒店比价 Markdown 内容
    
    Args:
        hotel_name: 酒店名称
        destination: 目的地
        
    Returns:
        Markdown 格式的比价信息
    """
    monitor = PricingMonitor()
    
    # 获取多平台价格
    prices = monitor.get_multi_platform_prices(hotel_name, destination)
    
    # 获取价格洞察
    insight = monitor.check_price(hotel_name, destination)
    
    # 生成 Markdown
    lines = [f"💰 **{hotel_name}** 比价建议\n"]
    
    # 价格对比
    for item in prices:
        lines.append(f"- {item['platform']}: ¥{item['price']}/晚")
    
    # 建议
    if insight:
        lines.append(f"\n💡 **建议**: {insight.suggestion}")
    
    return "\n".join(lines)


# ========== 测试代码 ==========
if __name__ == '__main__':
    monitor = PricingMonitor()
    
    test_hotels = [
        "海口朗廷酒店",
        "三亚海棠湾喜来登",
        "杭州西湖国宾馆"
    ]
    
    print("="*60)
    print("测试价格监控")
    print("="*60)
    
    for hotel in test_hotels:
        print(f"\n【{hotel}】")
        
        # 单个洞察
        insight = monitor.check_price(hotel, "海口")
        if insight:
            print(f"  平台: {insight.platform}")
            print(f"  价格: ¥{insight.current_price}")
            print(f"  趋势: {insight.trend}")
            print(f"  建议: {insight.suggestion}")
        
        # 多平台对比
        print("\n  多平台价格:")
        prices = monitor.get_multi_platform_prices(hotel, "海口")
        for p in prices:
            print(f"    - {p['platform']}: ¥{p['price']}")
    
    print("\n" + "="*60)
    print("测试 Markdown 生成")
    print("="*60)
    markdown = compare_hotel_prices("海口朗廷酒店", "海口")
    print(markdown)
