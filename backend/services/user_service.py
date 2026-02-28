"""
用户服务 - 用户管理和历史记录
简单版本：手机号登录，本地存储
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from loguru import logger


class UserService:
    """用户服务"""
    
    def __init__(self, data_dir: str = "/root/clawd/wildtrip/data/users"):
        """初始化用户服务"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 用户数据文件
        self.users_file = self.data_dir / "users.json"
        self.guides_file = self.data_dir / "user_guides.json"
        
        # 加载数据
        self.users = self._load_users()
        self.user_guides = self._load_guides()
        
        logger.info(f"✅ 用户服务初始化完成 | 用户数: {len(self.users)}")
    
    def _load_users(self) -> dict:
        """加载用户数据"""
        if self.users_file.exists():
            return json.loads(self.users_file.read_text(encoding='utf-8'))
        return {}
    
    def _save_users(self):
        """保存用户数据"""
        self.users_file.write_text(
            json.dumps(self.users, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
    
    def _load_guides(self) -> dict:
        """加载用户攻略数据"""
        if self.guides_file.exists():
            return json.loads(self.guides_file.read_text(encoding='utf-8'))
        return {}
    
    def _save_guides(self):
        """保存用户攻略数据"""
        self.guides_file.write_text(
            json.dumps(self.user_guides, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
    
    def create_or_get_user(self, phone: str, nickname: str = None) -> dict:
        """
        创建或获取用户（手机号登录，保留兼容）

        Args:
            phone: 手机号
            nickname: 昵称（可选）

        Returns:
            用户信息
        """
        # 生成用户ID（手机号hash）
        user_id = hashlib.md5(phone.encode()).hexdigest()[:16]

        if user_id not in self.users:
            # 创建新用户
            self.users[user_id] = {
                'user_id': user_id,
                'phone': phone[-4:],  # 只保存后4位
                'nickname': nickname or f"用户{phone[-4:]}",
                'created_at': datetime.now().isoformat(),
                'last_login': datetime.now().isoformat(),
                'guide_count': 0
            }
            self._save_users()
            logger.info(f"✅ 创建新用户: {user_id}")
        else:
            # 更新登录时间
            self.users[user_id]['last_login'] = datetime.now().isoformat()
            self._save_users()

        return self.users[user_id]

    def create_or_get_user_by_openid(self, openid: str, nickname: str = None) -> dict:
        """
        通过微信openid创建或获取用户（小程序登录）

        Args:
            openid: 微信openid
            nickname: 昵称（可选）

        Returns:
            用户信息
        """
        # 生成用户ID（openid hash）
        user_id = hashlib.md5(openid.encode()).hexdigest()[:16]

        if user_id not in self.users:
            # 创建新用户
            short_id = openid[-4:] if len(openid) >= 4 else openid
            self.users[user_id] = {
                'user_id': user_id,
                'openid': openid,
                'nickname': nickname or f"野游侠{short_id}",
                'created_at': datetime.now().isoformat(),
                'last_login': datetime.now().isoformat(),
                'guide_count': 0
            }
            self._save_users()
            logger.info(f"✅ 创建新用户(微信): {user_id}")
        else:
            # 更新登录时间
            self.users[user_id]['last_login'] = datetime.now().isoformat()
            # 确保旧用户也有openid字段
            if 'openid' not in self.users[user_id]:
                self.users[user_id]['openid'] = openid
            self._save_users()

        return self.users[user_id]
    
    def save_user_guide(self, user_id: str, guide_data: dict) -> str:
        """
        保存用户的攻略
        
        Args:
            user_id: 用户ID
            guide_data: 攻略数据
            
        Returns:
            guide_id
        """
        # 生成攻略ID
        guide_id = hashlib.md5(
            f"{user_id}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        # 保存攻略
        if user_id not in self.user_guides:
            self.user_guides[user_id] = []
        
        guide_record = {
            'guide_id': guide_id,
            'user_id': user_id,
            'query': guide_data.get('query', ''),
            'mode': guide_data.get('mode', 'full'),
            'content': guide_data.get('content', ''),
            'stats': guide_data.get('stats', {}),
            'seo_url': guide_data.get('seo_url'),
            'created_at': datetime.now().isoformat(),
            'favorite': False
        }
        
        self.user_guides[user_id].append(guide_record)
        self._save_guides()
        
        # 更新用户攻略计数
        if user_id in self.users:
            self.users[user_id]['guide_count'] = len(self.user_guides[user_id])
            self._save_users()
        
        logger.info(f"✅ 保存用户攻略: {user_id} | {guide_id}")
        
        return guide_id
    
    def get_user_guides(self, user_id: str, limit: int = 50) -> List[dict]:
        """
        获取用户的历史攻略
        
        Args:
            user_id: 用户ID
            limit: 返回数量
            
        Returns:
            攻略列表（按时间倒序）
        """
        guides = self.user_guides.get(user_id, [])
        
        # 按时间倒序
        guides = sorted(guides, key=lambda x: x['created_at'], reverse=True)
        
        return guides[:limit]
    
    def get_guide_by_id(self, user_id: str, guide_id: str) -> Optional[dict]:
        """
        获取单个攻略
        
        Args:
            user_id: 用户ID
            guide_id: 攻略ID
            
        Returns:
            攻略数据（如果存在）
        """
        guides = self.user_guides.get(user_id, [])
        
        for guide in guides:
            if guide['guide_id'] == guide_id:
                return guide
        
        return None
    
    def delete_guide(self, user_id: str, guide_id: str) -> bool:
        """
        删除攻略
        
        Args:
            user_id: 用户ID
            guide_id: 攻略ID
            
        Returns:
            是否成功
        """
        if user_id not in self.user_guides:
            return False
        
        # 查找并删除
        guides = self.user_guides[user_id]
        for i, guide in enumerate(guides):
            if guide['guide_id'] == guide_id:
                guides.pop(i)
                self._save_guides()
                
                # 更新计数
                if user_id in self.users:
                    self.users[user_id]['guide_count'] = len(guides)
                    self._save_users()
                
                logger.info(f"🗑️ 删除攻略: {user_id} | {guide_id}")
                return True
        
        return False
    
    def toggle_favorite(self, user_id: str, guide_id: str) -> bool:
        """
        切换收藏状态
        
        Args:
            user_id: 用户ID
            guide_id: 攻略ID
            
        Returns:
            新的收藏状态
        """
        guides = self.user_guides.get(user_id, [])
        
        for guide in guides:
            if guide['guide_id'] == guide_id:
                guide['favorite'] = not guide.get('favorite', False)
                self._save_guides()
                logger.info(f"⭐ 切换收藏: {user_id} | {guide_id} | {guide['favorite']}")
                return guide['favorite']
        
        return False
    
    def get_stats(self) -> dict:
        """
        获取统计数据
        
        Returns:
            统计信息
        """
        total_users = len(self.users)
        total_guides = sum(len(guides) for guides in self.user_guides.values())
        
        # 最近7天新增用户
        from datetime import timedelta
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        
        new_users_week = sum(
            1 for user in self.users.values()
            if datetime.fromisoformat(user['created_at']) > week_ago
        )
        
        return {
            'total_users': total_users,
            'total_guides': total_guides,
            'new_users_week': new_users_week,
            'avg_guides_per_user': round(total_guides / total_users, 2) if total_users > 0 else 0
        }


# 单例
_user_service_instance = None


def get_user_service() -> UserService:
    """获取用户服务实例（单例模式）"""
    global _user_service_instance
    
    if _user_service_instance is None:
        _user_service_instance = UserService()
    
    return _user_service_instance


# 测试
if __name__ == "__main__":
    service = UserService()
    
    # 创建用户
    user = service.create_or_get_user("13800138000", "测试用户")
    print("用户信息:", user)
    
    # 保存攻略
    guide_id = service.save_user_guide(user['user_id'], {
        'query': '上海3天游',
        'content': '# 上海攻略\n...',
        'stats': {'word_count': 1000}
    })
    print("攻略ID:", guide_id)
    
    # 查询历史
    guides = service.get_user_guides(user['user_id'])
    print(f"历史攻略: {len(guides)}篇")
    
    # 统计
    stats = service.get_stats()
    print("统计:", stats)
