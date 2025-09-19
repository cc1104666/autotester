-- 初始化数据库
CREATE DATABASE test_platform;

-- 切换到test_platform数据库
\c test_platform;

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 创建初始管理员用户（将在应用启动时通过SQLAlchemy创建表）
-- 这个脚本主要用于数据库初始化
