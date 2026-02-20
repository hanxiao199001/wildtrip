"""
野游记全局状态对象 (Global Trip State)
所有 Agent 共享的结构化状态
"""

from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field


class UserPreferences(BaseModel):
    """用户偏好"""
    has_kids: bool = False
    kids_ages: List[int] = []
    budget_level: str = 'mid'  # low/mid/high
    travel_style: List[str] = []  # culture/nature/food/relax
    equipment: List[str] = []  # camera/drone/etc
    mobility: str = 'normal'  # normal/limited
    dietary: List[str] = []  # vegetarian/halal/etc


class TripRequirements(BaseModel):
    """行程需求"""
    destination: str
    days: int
    budget: Optional[int] = None
    start_date: Optional[str] = None
    travelers: int = 1
    purpose: str = 'leisure'  # leisure/business/family
    

class HotelRecommendation(BaseModel):
    """酒店推荐"""
    name: str
    price: int
    location: str
    features: List[str]
    meituan_link: str
    feizhu_link: str
    reason: str  # 为什么推荐


class RestaurantRecommendation(BaseModel):
    """餐厅推荐"""
    name: str
    cuisine: str
    price_per_person: int
    dishes: List[str]
    meituan_link: str
    reason: str


class DailyItinerary(BaseModel):
    """每日行程"""
    day: int
    theme: str  # 当天主题
    morning: str
    lunch: RestaurantRecommendation
    afternoon: str
    dinner: RestaurantRecommendation
    accommodation: Optional[HotelRecommendation] = None
    wild_tips: List[str] = []  # 野路子小贴士


class PricingInsight(BaseModel):
    """价格洞察"""
    hotel_name: str
    platform: str  # meituan/feizhu/ctrip
    current_price: int
    trend: str  # rising/falling/stable
    suggestion: str  # 建议何时订


class TripState(BaseModel):
    """
    野游记全局状态对象
    
    这是所有 Agent 共享的"流水线产品"
    每个 Agent 只负责填充/更新自己负责的部分
    """
    
    # ========== 用户输入 ==========
    original_query: str  # 原始查询
    user_id: Optional[str] = None
    session_id: str
    
    # ========== 理解阶段 (Profile Agent) ==========
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    requirements: TripRequirements
    
    # ========== 规划阶段 (Wild-Routing Agent) ==========
    itinerary: List[DailyItinerary] = []
    hotels: List[HotelRecommendation] = []
    restaurants: List[RestaurantRecommendation] = []
    wild_places: List[Dict] = []  # 小众宝藏地点
    
    # ========== 比价阶段 (Pricing Agent) ==========
    pricing_insights: List[PricingInsight] = []
    best_booking_time: Optional[str] = None
    
    # ========== 内容生成阶段 (Content Agent) ==========
    markdown_content: Optional[str] = None
    xiaohongshu_content: Optional[str] = None
    
    # ========== 路由控制 (Gemini 建议) ==========
    next_agent: str = 'profile'  # 当前应该执行哪个 Agent
    is_finished: bool = False  # 是否完成
    
    # ========== 元数据 ==========
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    status: str = 'pending'  # pending/planning/pricing/completed
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def to_json(self) -> dict:
        """导出为 JSON (用于存储和传递)"""
        return self.dict()
    
    @classmethod
    def from_json(cls, data: dict):
        """从 JSON 恢复状态"""
        return cls(**data)
    
    def get_context_for_agent(self, agent_name: str) -> dict:
        """
        为特定 Agent 提取相关上下文
        
        避免"鸡同鸭讲",每个 Agent 只看到自己需要的信息
        """
        if agent_name == 'profile':
            return {
                'query': self.original_query,
                'previous_preferences': self.preferences.dict() if self.preferences else None
            }
        
        elif agent_name == 'wild_routing':
            return {
                'destination': self.requirements.destination,
                'days': self.requirements.days,
                'budget': self.requirements.budget,
                'preferences': self.preferences.dict(),
                'travelers': self.requirements.travelers
            }
        
        elif agent_name == 'pricing':
            return {
                'hotels': [h.dict() for h in self.hotels],
                'destination': self.requirements.destination,
                'check_in_date': self.requirements.start_date
            }
        
        elif agent_name == 'content':
            return {
                'itinerary': [d.dict() for d in self.itinerary],
                'hotels': [h.dict() for h in self.hotels],
                'restaurants': [r.dict() for r in self.restaurants],
                'pricing_insights': [p.dict() for p in self.pricing_insights]
            }
        
        return {}
