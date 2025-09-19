from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine
from pathlib import Path

from core.config import settings
from core.database import Base, engine
from api.v1 import auth, projects, test_cases, executions

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    description="智能自动化测试平台后端服务",
    version="1.0.0",
    debug=settings.DEBUG
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建必要的目录
Path("./allure-results").mkdir(exist_ok=True)
Path("./allure-reports").mkdir(exist_ok=True)
Path("./screenshots").mkdir(exist_ok=True)
Path("./logs").mkdir(exist_ok=True)
Path("./static").mkdir(exist_ok=True)

# 静态文件服务
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/reports", StaticFiles(directory="allure-reports"), name="reports")

# 注册路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["项目管理"])
app.include_router(test_cases.router, prefix="/api/v1", tags=["测试用例"])
app.include_router(executions.router, prefix="/api/v1", tags=["测试执行"])

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/")
async def root():
    return {"message": "欢迎使用自动化测试平台API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.DEBUG)
