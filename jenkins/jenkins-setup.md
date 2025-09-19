# Jenkins 配置指南

## 前置要求

### 1. Jenkins 插件安装
需要安装以下插件：
- Pipeline
- Docker Pipeline
- Allure
- Email Extension
- Git
- HTML Publisher
- JUnit
- Trivy

### 2. 系统工具配置

#### Docker
```bash
# 确保Jenkins用户可以访问Docker
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

#### Allure
```bash
# 安装Allure命令行工具
wget -O allure.tgz https://github.com/allure-framework/allure2/releases/download/2.24.1/allure-2.24.1.tgz
tar -xzf allure.tgz
sudo mv allure-2.24.1 /opt/allure
sudo ln -s /opt/allure/bin/allure /usr/local/bin/allure
```

#### Trivy（安全扫描）
```bash
# 安装Trivy
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
sudo apt-get update
sudo apt-get install trivy
```

## Jenkins 任务配置

### 1. 创建多分支流水线任务

1. 在Jenkins中点击"新建任务"
2. 选择"多分支流水线"
3. 输入任务名称：`test-platform`

### 2. 配置源代码管理

1. 选择Git
2. 输入仓库URL
3. 配置认证凭据
4. 分支发现策略：
   - 所有分支
   - 排除已合并的PR

### 3. 构建触发器

1. 配置Webhook（推荐）
2. 或定时构建：`H/5 * * * *`（每5分钟检查一次）

### 4. 流水线配置

- 定义：来自SCM的Pipeline script
- 脚本路径：`Jenkinsfile`

## 凭据配置

### 1. 数据库凭据
```
ID: postgres-credentials
类型: Username with password
用户名: postgres
密码: your-postgres-password
```

### 2. Docker Registry凭据（如果使用私有仓库）
```
ID: docker-registry-credentials
类型: Username with password
用户名: your-registry-username
密码: your-registry-password
```

### 3. 邮件配置
在"系统管理" -> "系统配置" -> "扩展邮件通知"中配置：
- SMTP服务器
- 默认发件人邮箱
- 认证信息

## 环境配置

### 1. 开发环境 (docker-compose.yml)
默认配置，用于本地开发

### 2. 测试环境 (docker-compose.staging.yml)
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: test_platform_staging
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "5434:5432"
    networks:
      - staging-network

  redis:
    image: redis:7-alpine
    ports:
      - "6380:6379"
    networks:
      - staging-network

  backend:
    image: ${BACKEND_IMAGE}
    environment:
      DATABASE_URL: postgresql://postgres:${POSTGRES_PASSWORD}@postgres:5432/test_platform_staging
      REDIS_URL: redis://redis:6379
      SECRET_KEY: ${SECRET_KEY}
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      DEBUG: "false"
    ports:
      - "8001:8000"
    networks:
      - staging-network

  frontend:
    image: ${FRONTEND_IMAGE}
    ports:
      - "8081:80"
    networks:
      - staging-network

networks:
  staging-network:
    driver: bridge
```

### 3. 生产环境 (docker-compose.prod.yml)
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: test_platform
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_prod_data:/var/lib/postgresql/data
    networks:
      - prod-network
    restart: always

  redis:
    image: redis:7-alpine
    volumes:
      - redis_prod_data:/data
    networks:
      - prod-network
    restart: always

  backend:
    image: ${BACKEND_IMAGE}
    environment:
      DATABASE_URL: postgresql://postgres:${POSTGRES_PASSWORD}@postgres:5432/test_platform
      REDIS_URL: redis://redis:6379
      SECRET_KEY: ${SECRET_KEY}
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      DEBUG: "false"
    volumes:
      - allure_prod_reports:/app/allure-reports
      - logs_prod:/app/logs
    networks:
      - prod-network
    restart: always

  frontend:
    image: ${FRONTEND_IMAGE}
    ports:
      - "80:80"
    networks:
      - prod-network
    restart: always

volumes:
  postgres_prod_data:
  redis_prod_data:
  allure_prod_reports:
  logs_prod:

networks:
  prod-network:
    driver: bridge
```

## 监控和告警

### 1. 健康检查接口
- 后端: `http://localhost:8000/health`
- 前端: `http://localhost/`

### 2. 日志监控
```bash
# 查看应用日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 查看系统资源
docker stats
```

### 3. 数据库备份
```bash
# 自动备份脚本
#!/bin/bash
BACKUP_DIR="/backup/postgres"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

docker-compose exec postgres pg_dump -U postgres test_platform > $BACKUP_DIR/backup_$DATE.sql

# 保留最近7天的备份
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
```

## 故障排除

### 1. 常见问题

#### Jenkins无法访问Docker
```bash
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

#### 内存不足
```bash
# 在Jenkins启动参数中增加内存
-Xmx2g -Xms1g
```

#### 权限问题
```bash
# 确保Jenkins用户有必要的权限
sudo chown -R jenkins:jenkins /var/lib/jenkins
```

### 2. 调试技巧

1. 查看构建日志
2. 使用Pipeline Syntax生成器
3. 在Jenkinsfile中添加调试输出
4. 使用Blue Ocean界面查看流水线

## 最佳实践

1. **分支策略**：
   - main分支自动部署到生产环境
   - develop分支自动部署到测试环境
   - feature分支只运行测试

2. **安全考虑**：
   - 使用凭据管理敏感信息
   - 定期更新Jenkins和插件
   - 启用安全扫描

3. **性能优化**：
   - 使用并行构建
   - 缓存依赖
   - 定期清理工作区

4. **通知机制**：
   - 构建失败时立即通知
   - 定期发送构建报告
   - 集成到团队沟通工具

## 扩展功能

### 1. SonarQube集成
代码质量分析和技术债务管理

### 2. Prometheus + Grafana
应用性能监控和指标可视化

### 3. ELK Stack
日志聚合和分析

### 4. Kubernetes部署
容器编排和自动扩缩容
