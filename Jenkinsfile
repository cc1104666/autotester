pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'localhost:5000'
        PROJECT_NAME = 'test-platform'
        POSTGRES_CREDENTIALS = credentials('postgres-credentials')
        COMPOSE_PROJECT_NAME = 'test-platform'
    }
    
    stages {
        stage('代码检出') {
            steps {
                echo '开始代码检出...'
                checkout scm
                
                script {
                    env.BUILD_VERSION = sh(
                        script: "echo ${env.BUILD_NUMBER}-${env.GIT_COMMIT.take(8)}",
                        returnStdout: true
                    ).trim()
                }
                
                echo "构建版本: ${env.BUILD_VERSION}"
            }
        }
        
        stage('环境准备') {
            parallel {
                stage('后端环境') {
                    steps {
                        echo '准备后端环境...'
                        dir('backend') {
                            sh '''
                                python3 -m venv venv
                                . venv/bin/activate
                                pip install --upgrade pip
                                pip install -r requirements.txt
                            '''
                        }
                    }
                }
                
                stage('前端环境') {
                    steps {
                        echo '准备前端环境...'
                        dir('frontend') {
                            sh '''
                                npm ci
                                npm audit --audit-level=high
                            '''
                        }
                    }
                }
            }
        }
        
        stage('代码质量检查') {
            parallel {
                stage('后端代码检查') {
                    steps {
                        echo '检查后端代码质量...'
                        dir('backend') {
                            sh '''
                                . venv/bin/activate
                                
                                # 代码格式检查
                                python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
                                
                                # 类型检查
                                python -m mypy . --ignore-missing-imports || true
                            '''
                        }
                    }
                }
                
                stage('前端代码检查') {
                    steps {
                        echo '检查前端代码质量...'
                        dir('frontend') {
                            sh '''
                                # TypeScript编译检查
                                npm run build --if-present
                                
                                # 代码规范检查
                                npm run lint --if-present || true
                            '''
                        }
                    }
                }
            }
        }
        
        stage('单元测试') {
            parallel {
                stage('后端单元测试') {
                    steps {
                        echo '运行后端单元测试...'
                        dir('backend') {
                            sh '''
                                . venv/bin/activate
                                export PYTHONPATH=$PWD
                                
                                # 运行单元测试
                                python -m pytest tests/test_*.py -v \
                                    --junitxml=test-results.xml \
                                    --cov=. \
                                    --cov-report=html \
                                    --cov-report=xml \
                                    -m "not ui"
                            '''
                        }
                    }
                    post {
                        always {
                            publishTestResults testResultsPattern: 'backend/test-results.xml'
                            publishHTML([
                                allowMissing: false,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: 'backend/htmlcov',
                                reportFiles: 'index.html',
                                reportName: 'Backend Coverage Report'
                            ])
                        }
                    }
                }
                
                stage('前端单元测试') {
                    steps {
                        echo '运行前端单元测试...'
                        dir('frontend') {
                            sh '''
                                npm test -- --coverage --watchAll=false --testResultsProcessor=jest-junit
                            '''
                        }
                    }
                    post {
                        always {
                            publishTestResults testResultsPattern: 'frontend/junit.xml'
                            publishHTML([
                                allowMissing: false,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: 'frontend/coverage/lcov-report',
                                reportFiles: 'index.html',
                                reportName: 'Frontend Coverage Report'
                            ])
                        }
                    }
                }
            }
        }
        
        stage('Docker构建') {
            parallel {
                stage('构建后端镜像') {
                    steps {
                        echo '构建后端Docker镜像...'
                        script {
                            def backendImage = docker.build(
                                "${DOCKER_REGISTRY}/${PROJECT_NAME}-backend:${BUILD_VERSION}",
                                "-f docker/Dockerfile.backend ."
                            )
                            backendImage.push()
                            backendImage.push("latest")
                        }
                    }
                }
                
                stage('构建前端镜像') {
                    steps {
                        echo '构建前端Docker镜像...'
                        script {
                            def frontendImage = docker.build(
                                "${DOCKER_REGISTRY}/${PROJECT_NAME}-frontend:${BUILD_VERSION}",
                                "-f docker/Dockerfile.frontend ."
                            )
                            frontendImage.push()
                            frontendImage.push("latest")
                        }
                    }
                }
            }
        }
        
        stage('集成测试') {
            steps {
                echo '运行集成测试...'
                script {
                    try {
                        // 启动测试环境
                        sh '''
                            # 创建测试环境的docker-compose文件
                            cp docker-compose.yml docker-compose.test.yml
                            
                            # 修改配置为测试环境
                            sed -i 's/test_platform/test_platform_test/g' docker-compose.test.yml
                            sed -i 's/5432:5432/5433:5432/g' docker-compose.test.yml
                            sed -i 's/8000:8000/8001:8000/g' docker-compose.test.yml
                            sed -i 's/80:80/8080:80/g' docker-compose.test.yml
                            
                            # 启动测试环境
                            docker-compose -f docker-compose.test.yml up -d
                            
                            # 等待服务启动
                            sleep 60
                            
                            # 检查服务状态
                            docker-compose -f docker-compose.test.yml ps
                        '''
                        
                        // 运行集成测试
                        sh '''
                            # 运行API集成测试
                            docker-compose -f docker-compose.test.yml exec -T backend \
                                python -m pytest tests/ -v \
                                --alluredir=/app/allure-results \
                                -m "api" || true
                            
                            # 运行UI集成测试
                            docker-compose -f docker-compose.test.yml exec -T backend \
                                python -m pytest tests/ui/ -v \
                                --alluredir=/app/allure-results \
                                -m "ui" || true
                        '''
                        
                        // 生成测试报告
                        sh '''
                            # 复制测试结果
                            docker cp test-platform-backend:/app/allure-results ./allure-results || true
                            
                            # 生成Allure报告
                            if [ -d "./allure-results" ] && [ "$(ls -A ./allure-results)" ]; then
                                allure generate ./allure-results -o ./allure-reports --clean || true
                            fi
                        '''
                        
                    } finally {
                        // 清理测试环境
                        sh '''
                            docker-compose -f docker-compose.test.yml down -v || true
                            docker system prune -f || true
                        '''
                    }
                }
            }
            post {
                always {
                    // 发布Allure报告
                    allure([
                        includeProperties: false,
                        jdk: '',
                        properties: [],
                        reportBuildPolicy: 'ALWAYS',
                        results: [[path: 'allure-results']]
                    ])
                    
                    // 存档构建产物
                    archiveArtifacts artifacts: 'allure-reports/**/*', allowEmptyArchive: true
                }
            }
        }
        
        stage('安全扫描') {
            parallel {
                stage('镜像安全扫描') {
                    steps {
                        echo '执行Docker镜像安全扫描...'
                        script {
                            // 使用Trivy进行安全扫描
                            sh '''
                                # 扫描后端镜像
                                trivy image --exit-code 0 --severity HIGH,CRITICAL \
                                    ${DOCKER_REGISTRY}/${PROJECT_NAME}-backend:${BUILD_VERSION} || true
                                
                                # 扫描前端镜像
                                trivy image --exit-code 0 --severity HIGH,CRITICAL \
                                    ${DOCKER_REGISTRY}/${PROJECT_NAME}-frontend:${BUILD_VERSION} || true
                            '''
                        }
                    }
                }
                
                stage('依赖安全扫描') {
                    steps {
                        echo '执行依赖安全扫描...'
                        dir('backend') {
                            sh '''
                                . venv/bin/activate
                                pip install safety
                                safety check --json --output safety-report.json || true
                            '''
                        }
                        dir('frontend') {
                            sh '''
                                npm audit --json > npm-audit.json || true
                            '''
                        }
                    }
                }
            }
        }
        
        stage('部署到测试环境') {
            when {
                anyOf {
                    branch 'develop'
                    branch 'feature/*'
                }
            }
            steps {
                echo '部署到测试环境...'
                sh '''
                    # 更新测试环境配置
                    export BACKEND_IMAGE=${DOCKER_REGISTRY}/${PROJECT_NAME}-backend:${BUILD_VERSION}
                    export FRONTEND_IMAGE=${DOCKER_REGISTRY}/${PROJECT_NAME}-frontend:${BUILD_VERSION}
                    
                    # 部署到测试环境
                    docker-compose -f docker-compose.staging.yml up -d
                '''
            }
        }
        
        stage('部署到生产环境') {
            when {
                branch 'main'
            }
            steps {
                script {
                    // 需要人工确认
                    def userInput = input(
                        id: 'userInput',
                        message: '是否部署到生产环境？',
                        parameters: [
                            choice(
                                choices: ['部署', '取消'],
                                description: '选择操作',
                                name: 'deployAction'
                            )
                        ]
                    )
                    
                    if (userInput == '部署') {
                        echo '部署到生产环境...'
                        sh '''
                            # 创建备份
                            docker-compose -f docker-compose.prod.yml exec postgres \
                                pg_dump -U postgres test_platform > backup_$(date +%Y%m%d_%H%M%S).sql
                            
                            # 更新生产环境配置
                            export BACKEND_IMAGE=${DOCKER_REGISTRY}/${PROJECT_NAME}-backend:${BUILD_VERSION}
                            export FRONTEND_IMAGE=${DOCKER_REGISTRY}/${PROJECT_NAME}-frontend:${BUILD_VERSION}
                            
                            # 滚动更新
                            docker-compose -f docker-compose.prod.yml up -d --no-deps backend
                            sleep 30
                            docker-compose -f docker-compose.prod.yml up -d --no-deps frontend
                            
                            # 健康检查
                            timeout 300 bash -c 'until curl -f http://localhost/health; do sleep 5; done'
                        '''
                    } else {
                        echo '用户取消了生产环境部署'
                    }
                }
            }
        }
        
        stage('烟雾测试') {
            when {
                branch 'main'
            }
            steps {
                echo '执行生产环境烟雾测试...'
                sh '''
                    # 基础健康检查
                    curl -f http://localhost/health
                    
                    # API可用性检查
                    curl -f http://localhost/api/v1/auth/login -X POST \
                        -H "Content-Type: application/json" \
                        -d '{"username":"test","password":"test"}' || true
                    
                    # 前端页面检查
                    curl -f http://localhost/ | grep "自动化测试平台"
                '''
            }
        }
    }
    
    post {
        always {
            echo '清理工作区...'
            cleanWs()
        }
        
        success {
            echo '构建成功！'
            emailext (
                subject: "✅ 构建成功: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: """
                构建成功完成！
                
                项目: ${env.JOB_NAME}
                构建号: ${env.BUILD_NUMBER}
                版本: ${env.BUILD_VERSION}
                分支: ${env.GIT_BRANCH}
                提交: ${env.GIT_COMMIT}
                
                查看详情: ${env.BUILD_URL}
                查看报告: ${env.BUILD_URL}allure/
                """,
                to: "${env.CHANGE_AUTHOR_EMAIL ?: 'dev-team@example.com'}"
            )
        }
        
        failure {
            echo '构建失败！'
            emailext (
                subject: "❌ 构建失败: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: """
                构建失败！
                
                项目: ${env.JOB_NAME}
                构建号: ${env.BUILD_NUMBER}
                分支: ${env.GIT_BRANCH}
                提交: ${env.GIT_COMMIT}
                
                查看详情: ${env.BUILD_URL}
                查看日志: ${env.BUILD_URL}console
                """,
                to: "${env.CHANGE_AUTHOR_EMAIL ?: 'dev-team@example.com'}"
            )
        }
        
        unstable {
            echo '构建不稳定！'
            emailext (
                subject: "⚠️ 构建不稳定: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: """
                构建不稳定，存在测试失败！
                
                项目: ${env.JOB_NAME}
                构建号: ${env.BUILD_NUMBER}
                分支: ${env.GIT_BRANCH}
                
                查看详情: ${env.BUILD_URL}
                查看测试报告: ${env.BUILD_URL}allure/
                """,
                to: "${env.CHANGE_AUTHOR_EMAIL ?: 'dev-team@example.com'}"
            )
        }
    }
}
