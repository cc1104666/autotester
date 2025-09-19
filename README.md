# 智能自动化测试平台

一个基于现代技术栈构建的全栈自动化测试平台，支持API接口测试和UI自动化测试，提供可视化的测试管理界面、详细的测试报告以及完整的CI/CD集成能力。

## 🚀 技术栈

### 后端
- **Python 3.11+** + **FastAPI** - 高性能异步API框架
- **PostgreSQL 15+** - 可靠的关系型数据库
- **Redis** - 高性能缓存数据库
- **SQLAlchemy** - ORM框架
- **Alembic** - 数据库迁移工具

### 前端
- **React 18+** + **TypeScript** - 现代化UI框架
- **Ant Design** - 企业级UI组件库
- **React Router** - 前端路由管理
- **Axios** - HTTP客户端

### 测试框架
- **pytest** - Python测试框架
- **Playwright** - 现代Web UI自动化测试
- **Allure** - 测试报告框架
- **requests** - HTTP库

### 部署运维
- **Docker** + **Docker Compose** - 容器化部署
- **Jenkins** - CI/CD流水线
- **Nginx** - 反向代理和静态文件服务

## 📋 核心功能

### 🔐 用户管理
- 用户注册、登录、权限管理
- 基于JWT的身份认证
- 角色权限控制（管理员、测试人员、只读用户）

### 📊 项目管理
- 测试项目创建与配置
- 环境管理（开发、测试、生产）
- 项目成员管理

### 🧪 测试用例管理
- API测试用例编写与管理
- UI测试场景设计
- 测试数据管理
- 用例分组与标签

### ⚡ 测试执行引擎
- 分布式测试执行
- 并发测试支持
- 实时执行监控
- 失败重试机制

### 📈 报告与统计
- Allure报告集成
- 测试趋势分析
- 覆盖率统计
- 邮件通知

### 🔄 CI/CD集成
- Jenkins流水线集成
- Git仓库关联
- 自动触发测试
- 构建状态反馈

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端界面      │    │   后端API       │    │   数据库层      │
│   React + TS    │◄──►│   FastAPI       │◄──►│   PostgreSQL    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │   测试执行层    │              │
         └─────────────►│ pytest+Playwright│◄─────────────┘
                        └─────────────────┘
                                 │
                        ┌─────────────────┐
                        │   报告系统      │
                        │   Allure        │
                        └─────────────────┘
```

## 🚀 快速开始

### 环境要求
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- Git

### 1. 克隆项目
```bash
git clone <repository-url>
cd test-platform
```

### 2. 环境配置
```bash
# 复制环境配置文件
cp backend/.env.example backend/.env

# 编辑配置文件
vim backend/.env
```

### 3. 启动服务
```bash
# 使用Docker Compose启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps
```

### 4. 访问应用
- 前端界面: http://localhost
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

### 5. 创建管理员用户
```bash
# 进入后端容器
docker-compose exec backend python

# 在Python shell中创建管理员
from models.user import User
from core.database import SessionLocal
from core.security import get_password_hash

db = SessionLocal()
admin_user = User(
    username="admin",
    email="admin@example.com",
    password_hash=get_password_hash("admin123"),
    role="admin",
    is_active=True
)
db.add(admin_user)
db.commit()
exit()
```

## 🧪 运行测试

### 后端测试
```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 运行单元测试
pytest tests/ -v

# 运行带覆盖率的测试
pytest tests/ --cov=. --cov-report=html

# 运行特定标记的测试
pytest tests/ -m "api"  # 只运行API测试
pytest tests/ -m "ui"   # 只运行UI测试
```

### 前端测试
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 运行测试
npm test

# 运行带覆盖率的测试
npm test -- --coverage
```

### 集成测试
```bash
# 启动测试环境
docker-compose -f docker-compose.test.yml up -d

# 运行所有测试
pytest tests/ --alluredir=allure-results

# 生成Allure报告
allure generate allure-results -o allure-reports --clean
allure open allure-reports
```

## 📦 部署指南

### 开发环境
```bash
# 启动开发环境
docker-compose up -d
```

### 测试环境
```bash
# 启动测试环境
docker-compose -f docker-compose.staging.yml up -d
```

### 生产环境
```bash
# 启动生产环境
docker-compose -f docker-compose.prod.yml up -d
```

## 🔧 配置说明

### 后端配置
主要配置文件：`backend/.env`

```env
# 应用配置
SECRET_KEY=your-secret-key-here
DEBUG=false
APP_NAME=自动化测试平台

# 数据库配置
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/test_platform

# Redis配置
REDIS_URL=redis://localhost:6379

# JWT配置
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30
```

### 前端配置
主要配置文件：`frontend/package.json`

代理配置已设置为后端服务地址，生产环境通过Nginx反向代理。

## 📚 API文档

启动服务后，访问以下地址查看API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要API端点

#### 认证相关
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/register` - 用户注册
- `GET /api/v1/auth/me` - 获取当前用户信息

#### 项目管理
- `GET /api/v1/projects` - 获取项目列表
- `POST /api/v1/projects` - 创建项目
- `GET /api/v1/projects/{id}` - 获取项目详情
- `PUT /api/v1/projects/{id}` - 更新项目
- `DELETE /api/v1/projects/{id}` - 删除项目

#### 测试用例
- `GET /api/v1/projects/{id}/test-cases` - 获取测试用例列表
- `POST /api/v1/projects/{id}/test-cases` - 创建测试用例
- `PUT /api/v1/test-cases/{id}` - 更新测试用例
- `DELETE /api/v1/test-cases/{id}` - 删除测试用例

#### 测试执行
- `POST /api/v1/projects/{id}/execute` - 执行测试
- `GET /api/v1/executions/{id}` - 获取执行详情
- `GET /api/v1/projects/{id}/executions` - 获取执行历史

## 🔒 安全考虑

### 身份认证与授权
- JWT token认证
- 基于角色的访问控制（RBAC）
- 密码强度验证
- 会话超时管理

### 数据安全
- 数据库连接加密
- 敏感数据脱敏
- API参数校验
- SQL注入防护

### 网络安全
- HTTPS强制加密
- CORS配置
- 请求频率限制
- 防火墙规则

## 📊 监控和日志

### 应用监控
- 健康检查端点：`/health`
- 性能指标收集
- 错误率监控
- 响应时间统计

### 日志管理
```bash
# 查看应用日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 查看特定时间段的日志
docker-compose logs --since 2023-01-01T00:00:00 backend
```

### 数据库备份
```bash
# 手动备份
docker-compose exec postgres pg_dump -U postgres test_platform > backup.sql

# 自动备份脚本在jenkins/目录下
```

## 🛠️ 开发指南

### 项目结构
```
project/
├── backend/                 # 后端代码
│   ├── core/               # 核心模块（配置、数据库、安全）
│   ├── models/             # 数据模型
│   ├── schemas/            # API模式定义
│   ├── api/                # API路由
│   ├── services/           # 业务逻辑
│   └── utils/              # 工具函数
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── components/     # 通用组件
│   │   ├── pages/          # 页面组件
│   │   ├── hooks/          # 自定义Hook
│   │   ├── services/       # API服务
│   │   └── types/          # 类型定义
├── tests/                  # 测试代码
│   ├── api/               # API测试
│   └── ui/                # UI测试
├── docker/                 # Docker配置
├── jenkins/                # Jenkins配置
└── docs/                   # 文档
```

### 代码规范
- 后端：遵循PEP 8规范
- 前端：使用ESLint + Prettier
- 提交信息：遵循Conventional Commits

### 开发流程
1. 创建功能分支
2. 编写代码和测试
3. 提交PR
4. 代码审查
5. 合并到主分支
6. 自动部署

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系我们

- 项目地址：<repository-url>
- 问题反馈：<repository-url>/issues
- 邮箱：dev-team@example.com

## 🙏 致谢

感谢以下优秀的开源项目：
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://reactjs.org/)
- [Ant Design](https://ant.design/)
- [Playwright](https://playwright.dev/)
- [Allure](https://docs.qameta.io/allure/)
- [PostgreSQL](https://www.postgresql.org/)

## 📈 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 实现基础功能模块
- 支持API和UI测试
- Docker容器化部署
- Jenkins CI/CD集成

---

🎉 感谢使用智能自动化测试平台！如有问题，请随时提交Issue或联系我们。
