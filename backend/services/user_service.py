"""
用户服务
"""
from models import db, User
from datetime import datetime, timedelta
from loguru import logger


class UserService:
    """用户服务类"""
    
    @staticmethod
    def get_or_create_user(openid: str, unionid: str = None):
        """
        获取或创建用户
        
        Args:
            openid: 微信openid
            unionid: 微信unionid (可选)
        
        Returns:
            User对象
        """
        try:
            user = User.query.filter_by(openid=openid).first()
            
            if not user:
                user = User(
                    openid=openid,
                    unionid=unionid,
                    created_at=datetime.now()
                )
                db.session.add(user)
                db.session.commit()
                logger.info(f"✅ 创建新用户: {openid}")
            
            # 更新最后登录时间
            user.last_login_at = datetime.now()
            db.session.commit()
            
            return user
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ 获取/创建用户失败: {e}")
            raise
    
    @staticmethod
    def update_user_info(openid: str, nickname: str = None, avatar: str = None, gender: int = None):
        """更新用户信息"""
        try:
            user = User.query.filter_by(openid=openid).first()
            if not user:
                return False
            
            if nickname:
                user.nickname = nickname
            if avatar:
                user.avatar = avatar
            if gender is not None:
                user.gender = gender
            
            db.session.commit()
            logger.info(f"✅ 更新用户信息: {openid}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ 更新用户信息失败: {e}")
            return False
    
    @staticmethod
    def activate_vip(openid: str, duration_days: int):
        """
        激活VIP
        
        Args:
            openid: 用户openid
            duration_days: VIP时长(天)
        
        Returns:
            User对象
        """
        try:
            user = User.query.filter_by(openid=openid).first()
            if not user:
                # 用户不存在,自动创建
                user = UserService.get_or_create_user(openid)
            
            now = datetime.now()
            
            # 首次激活
            if not user.is_vip or not user.vip_expire_at:
                user.vip_activated_at = now
                user.vip_expire_at = now + timedelta(days=duration_days)
            else:
                # 续费: 从当前到期时间延长
                if user.vip_expire_at > now:
                    # VIP未过期,从到期时间延长
                    user.vip_expire_at += timedelta(days=duration_days)
                else:
                    # VIP已过期,从现在开始
                    user.vip_expire_at = now + timedelta(days=duration_days)
            
            user.is_vip = True
            user.order_count = (user.order_count or 0) + 1
            
            db.session.commit()
            
            logger.success(f"🎉 激活VIP成功: {openid} | +{duration_days}天 | 到期: {user.vip_expire_at.strftime('%Y-%m-%d')}")
            return user
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ 激活VIP失败: {e}")
            raise
    
    @staticmethod
    def check_vip_status(openid: str):
        """
        检查VIP状态
        
        Returns:
            dict: {
                'is_vip': bool,
                'expire_at': str,
                'days_left': int
            }
        """
        user = User.query.filter_by(openid=openid).first()
        
        if not user:
            return {
                'is_vip': False,
                'expire_at': None,
                'days_left': 0
            }
        
        # 检查是否过期
        now = datetime.now()
        if user.is_vip and user.vip_expire_at and user.vip_expire_at <= now:
            # VIP已过期,更新状态
            user.is_vip = False
            db.session.commit()
        
        return {
            'is_vip': user.is_vip,
            'expire_at': user.vip_expire_at.isoformat() if user.vip_expire_at else None,
            'days_left': user.vip_days_left()
        }
    
    @staticmethod
    def increment_generate_count(openid: str):
        """增加生成次数"""
        try:
            user = User.query.filter_by(openid=openid).first()
            if user:
                user.generate_count = (user.generate_count or 0) + 1
                db.session.commit()
        except Exception as e:
            logger.error(f"❌ 增加生成次数失败: {e}")
    
    @staticmethod
    def add_paid_amount(openid: str, amount: int):
        """增加累计消费"""
        try:
            user = User.query.filter_by(openid=openid).first()
            if user:
                user.total_paid = (user.total_paid or 0) + amount
                db.session.commit()
        except Exception as e:
            logger.error(f"❌ 增加累计消费失败: {e}")
    
    @staticmethod
    def get_vip_users(limit: int = 100):
        """获取VIP用户列表"""
        now = datetime.now()
        return User.query.filter(
            User.is_vip == True,
            User.vip_expire_at > now
        ).order_by(User.vip_expire_at.desc()).limit(limit).all()
    
    @staticmethod
    def expire_vip_users():
        """
        清理过期VIP (定时任务)
        返回清理数量
        """
        try:
            now = datetime.now()
            expired_users = User.query.filter(
                User.is_vip == True,
                User.vip_expire_at <= now
            ).all()
            
            count = 0
            for user in expired_users:
                user.is_vip = False
                count += 1
            
            db.session.commit()
            
            if count > 0:
                logger.info(f"✅ 清理过期VIP: {count}个")
            
            return count
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ 清理过期VIP失败: {e}")
            return 0
