#!/usr/bin/env python3
"""
创建管理员用户脚本
"""
import sys
import os

# 添加backend目录到Python路径
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

try:
    from models.user import User
    from core.database import SessionLocal
    from core.security import get_password_hash
    
    def create_admin_user():
        db = SessionLocal()
        try:
            # 检查是否已存在管理员
            existing_admin = db.query(User).filter(User.username == 'admin').first()
            if existing_admin:
                print("❌ 管理员用户已存在")
                return False
            
            # 创建管理员用户
            admin_user = User(
                username='admin',
                email='admin@example.com',
                password_hash=get_password_hash('admin123'),
                role='admin',
                is_active=True
            )
            
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            
            print("✅ 管理员用户创建成功!")
            print("   用户名: admin")
            print("   密码: admin123")
            print("   邮箱: admin@example.com")
            
            return True
            
        except Exception as e:
            print(f"❌ 创建管理员用户失败: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    if __name__ == "__main__":
        print("🔧 创建管理员用户...")
        create_admin_user()
        
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    print("请确保:")
    print("1. 已安装后端依赖: pip install -r backend/requirements.txt")
    print("2. 数据库服务已启动: docker-compose up -d postgres")
    print("3. 在项目根目录运行此脚本")
except Exception as e:
    print(f"❌ 执行失败: {e}")
