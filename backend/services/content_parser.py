"""
内容解析器
从 AI 生成的 Markdown 内容中提取结构化数据
"""

import re
from typing import List, Dict, Optional
from loguru import logger
from core.trip_state import HotelRecommendation, RestaurantRecommendation, DailyItinerary


def parse_itinerary(markdown_content: str) -> List[DailyItinerary]:
    """
    从 Markdown 内容中解析每日行程
    
    Args:
        markdown_content: AI 生成的完整攻略
        
    Returns:
        每日行程列表
    """
    itineraries = []
    
    try:
        # 匹配 Day X 的行程
        day_pattern = r'### 📅 Day (\d+)[:：](.+?)(?=### 📅 Day \d+|## 🍽️|$)'
        days = re.findall(day_pattern, markdown_content, re.DOTALL)
        
        for day_num, day_content in days:
            # 提取主题
            theme_match = re.search(r'> \*\*主题[:：]\*\* (.+)', day_content)
            theme = theme_match.group(1).strip() if theme_match else f"Day {day_num}"
            
            # 提取上午/下午/晚上活动
            morning_match = re.search(r'上午.*?[:：](.+?)(?=\n|中午|下午)', day_content, re.DOTALL)
            morning = morning_match.group(1).strip() if morning_match else ""
            
            afternoon_match = re.search(r'下午.*?[:：](.+?)(?=\n|晚上|## )', day_content, re.DOTALL)
            afternoon = afternoon_match.group(1).strip() if afternoon_match else ""
            
            # 创建行程对象（暂时不解析午餐/晚餐/住宿，后续完善）
            itinerary = DailyItinerary(
                day=int(day_num),
                theme=theme,
                morning=morning[:200] if morning else "",
                lunch=RestaurantRecommendation(
                    name="待解析",
                    cuisine="",
                    price_per_person=0,
                    dishes=[],
                    meituan_link="",
                    reason=""
                ),
                afternoon=afternoon[:200] if afternoon else "",
                dinner=RestaurantRecommendation(
                    name="待解析",
                    cuisine="",
                    price_per_person=0,
                    dishes=[],
                    meituan_link="",
                    reason=""
                ),
                wild_tips=[]
            )
            
            itineraries.append(itinerary)
            logger.info(f"✅ 解析 Day {day_num}: {theme}")
    
    except Exception as e:
        logger.error(f"❌ 解析行程失败: {e}")
    
    return itineraries


def parse_hotels(markdown_content: str, destination: str = "") -> List[HotelRecommendation]:
    """
    从 Markdown 内容中解析酒店推荐
    
    Args:
        markdown_content: AI 生成的完整攻略
        destination: 目的地城市
        
    Returns:
        酒店推荐列表
    """
    hotels = []
    
    try:
        # 匹配酒店推荐部分
        # 格式示例：
        # **酒店名称**
        # - 人均: ¥XXX/晚
        # - 地址: XXX
        # - 推荐理由: XXX
        
        hotel_pattern = r'\*\*(.+?酒店|.+?民宿|.+?客栈)\*\*\s*\n(.*?)(?=\n\*\*|## |$)'
        matches = re.findall(hotel_pattern, markdown_content, re.DOTALL)
        
        for hotel_name, hotel_info in matches:
            hotel_name = hotel_name.strip()
            
            # 提取价格
            price_match = re.search(r'[¥￥](\d+)', hotel_info)
            price = int(price_match.group(1)) if price_match else 0
            
            # 提取地址
            location_match = re.search(r'地址[:：](.+)', hotel_info)
            location = location_match.group(1).strip() if location_match else destination
            
            # 提取特色
            features = []
            if '泳池' in hotel_info:
                features.append('泳池')
            if '儿童' in hotel_info or '亲子' in hotel_info:
                features.append('亲子设施')
            if '早餐' in hotel_info:
                features.append('含早餐')
            if '海景' in hotel_info or '江景' in hotel_info:
                features.append('景观房')
            
            # 提取推荐理由
            reason_match = re.search(r'推荐理由[:：](.+)', hotel_info)
            reason = reason_match.group(1).strip() if reason_match else "性价比高"
            
            # 生成美团链接（占位）
            meituan_link = f"https://i.meituan.com/search?keyword={hotel_name}&ci=8"
            feizhu_link = f"https://www.fliggy.com/search?keyword={hotel_name}"
            
            hotel = HotelRecommendation(
                name=hotel_name,
                price=price,
                location=location,
                features=features,
                meituan_link=meituan_link,
                feizhu_link=feizhu_link,
                reason=reason[:100]
            )
            
            hotels.append(hotel)
            logger.info(f"✅ 解析酒店: {hotel_name}, ¥{price}")
    
    except Exception as e:
        logger.error(f"❌ 解析酒店失败: {e}")
    
    return hotels


def parse_restaurants(markdown_content: str, destination: str = "") -> List[RestaurantRecommendation]:
    """
    从 Markdown 内容中解析餐厅推荐
    
    Args:
        markdown_content: AI 生成的完整攻略
        destination: 目的地城市
        
    Returns:
        餐厅推荐列表
    """
    restaurants = []
    
    try:
        # 匹配餐厅推荐部分
        # 格式示例：
        # **餐厅名称**
        # - 人均: ¥XXX
        # - 推荐菜: XXX、XXX
        
        restaurant_pattern = r'\*\*(.+?(?:餐厅|饭店|小吃|粉店|面馆|海鲜|烧烤))\*\*\s*\n(.*?)(?=\n\*\*|## |$)'
        matches = re.findall(restaurant_pattern, markdown_content, re.DOTALL)
        
        for restaurant_name, restaurant_info in matches:
            restaurant_name = restaurant_name.strip()
            
            # 提取人均价格
            price_match = re.search(r'人均[:：][¥￥]?(\d+)', restaurant_info)
            price_per_person = int(price_match.group(1)) if price_match else 0
            
            # 提取菜系
            cuisine = "本地特色"
            if '海南' in restaurant_info:
                cuisine = "海南菜"
            elif '川菜' in restaurant_info or '辣' in restaurant_info:
                cuisine = "川菜"
            elif '粤菜' in restaurant_info:
                cuisine = "粤菜"
            elif '海鲜' in restaurant_name or '海鲜' in restaurant_info:
                cuisine = "海鲜"
            
            # 提取推荐菜品
            dishes = []
            dishes_match = re.search(r'推荐菜[:：](.+)', restaurant_info)
            if dishes_match:
                dishes_str = dishes_match.group(1)
                dishes = [d.strip() for d in re.split('[、，,]', dishes_str) if d.strip()]
            
            # 提取推荐理由
            reason_match = re.search(r'(?:推荐理由|野导游说)[:：](.+)', restaurant_info)
            reason = reason_match.group(1).strip() if reason_match else "本地人推荐"
            
            # 生成美团链接
            meituan_link = f"https://i.meituan.com/search?keyword={restaurant_name}&ci=8"
            
            restaurant = RestaurantRecommendation(
                name=restaurant_name,
                cuisine=cuisine,
                price_per_person=price_per_person,
                dishes=dishes[:5],  # 最多5个
                meituan_link=meituan_link,
                reason=reason[:100]
            )
            
            restaurants.append(restaurant)
            logger.info(f"✅ 解析餐厅: {restaurant_name}, 人均¥{price_per_person}")
    
    except Exception as e:
        logger.error(f"❌ 解析餐厅失败: {e}")
    
    return restaurants


def extract_wild_tips(markdown_content: str) -> List[str]:
    """
    提取"野路子"小贴士
    
    Args:
        markdown_content: 攻略内容
        
    Returns:
        小贴士列表
    """
    tips = []
    
    try:
        # 匹配 💡 Tips 部分
        tips_pattern = r'💡.*?Tips.*?[:：]\s*\n(.+?)(?=\n##|$)'
        matches = re.findall(tips_pattern, markdown_content, re.DOTALL)
        
        for match in matches:
            # 分行提取
            lines = [line.strip('- ').strip() for line in match.split('\n') if line.strip()]
            tips.extend(lines)
    
    except Exception as e:
        logger.error(f"❌ 提取 Tips 失败: {e}")
    
    return tips[:10]  # 最多10条


# ========== 测试代码 ==========
if __name__ == '__main__':
    # 测试用的 Markdown 内容
    test_content = """
### 📅 Day 1: 慢享海口老城

> **主题:** 探索骑楼老街，感受老海口风情

**上午:** 9:00-12:00 骑楼老街漫步，避开10点后的人流

**午餐:** 梅姨海南粉
- 人均: ¥15
- 推荐菜: 海南粉、椰子饼
- 野导游说: 本地人从小吃到大的味道

**下午:** 14:00-17:00 五公祠，人文历史

**晚餐:** 文昌鸡饭老店
- 人均: ¥50
- 推荐菜: 白切文昌鸡、鸡油饭

## 🏨 住宿推荐

**海口朗廷酒店**
- 价格: ¥680/晚
- 地址: 海口市龙华区
- 推荐理由: 无边泳池，儿童设施完善，含早餐
"""
    
    print("="*60)
    print("测试行程解析")
    print("="*60)
    itineraries = parse_itinerary(test_content)
    for itinerary in itineraries:
        print(f"Day {itinerary.day}: {itinerary.theme}")
        print(f"  上午: {itinerary.morning}")
        print(f"  下午: {itinerary.afternoon}")
    
    print("\n" + "="*60)
    print("测试酒店解析")
    print("="*60)
    hotels = parse_hotels(test_content, "海口")
    for hotel in hotels:
        print(f"{hotel.name}: ¥{hotel.price}/晚")
        print(f"  特色: {', '.join(hotel.features)}")
        print(f"  理由: {hotel.reason}")
    
    print("\n" + "="*60)
    print("测试餐厅解析")
    print("="*60)
    restaurants = parse_restaurants(test_content, "海口")
    for restaurant in restaurants:
        print(f"{restaurant.name}: 人均¥{restaurant.price_per_person}")
        print(f"  菜系: {restaurant.cuisine}")
        print(f"  推荐菜: {', '.join(restaurant.dishes)}")
