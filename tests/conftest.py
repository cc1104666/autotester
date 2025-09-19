import pytest
import asyncio
from typing import Generator, AsyncGenerator
from httpx import AsyncClient
from playwright.async_api import async_playwright, Browser, Page
from fastapi.testclient import TestClient
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app
from backend.core.database import SessionLocal, engine
from backend.models.user import User
from backend.core.security import get_password_hash

# 测试数据库配置
@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_client():
    """FastAPI测试客户端"""
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="session")
async def async_client():
    """异步HTTP客户端"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture(scope="session")
def db_session():
    """数据库会话"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="session")
def test_user(db_session):
    """创建测试用户"""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=get_password_hash("testpassword"),
        role="tester",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="session")
def admin_user(db_session):
    """创建管理员用户"""
    user = User(
        username="admin",
        email="admin@example.com",
        password_hash=get_password_hash("adminpassword"),
        role="admin",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="session")
async def browser() -> AsyncGenerator[Browser, None]:
    """Playwright浏览器实例"""
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        yield browser
        await browser.close()

@pytest.fixture
async def page(browser: Browser) -> AsyncGenerator[Page, None]:
    """Playwright页面实例"""
    page = await browser.new_page()
    yield page
    await page.close()

@pytest.fixture
def auth_headers(test_client, test_user):
    """获取认证头"""
    response = test_client.post("/api/v1/auth/login", data={
        "username": test_user.username,
        "password": "testpassword"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_auth_headers(test_client, admin_user):
    """获取管理员认证头"""
    response = test_client.post("/api/v1/auth/login", data={
        "username": admin_user.username,
        "password": "adminpassword"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
