import pytest
import allure
from fastapi.testclient import TestClient

@allure.feature("用户认证")
class TestAuth:
    
    @allure.story("用户登录")
    @pytest.mark.api
    def test_login_success(self, test_client: TestClient, test_user):
        """测试用户成功登录"""
        with allure.step("发送登录请求"):
            response = test_client.post("/api/v1/auth/login", data={
                "username": test_user.username,
                "password": "testpassword"
            })
        
        with allure.step("验证响应状态码"):
            assert response.status_code == 200
        
        with allure.step("验证响应内容"):
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
    
    @allure.story("用户登录")
    @pytest.mark.api
    def test_login_invalid_credentials(self, test_client: TestClient):
        """测试无效凭据登录"""
        with allure.step("发送无效登录请求"):
            response = test_client.post("/api/v1/auth/login", data={
                "username": "invalid",
                "password": "invalid"
            })
        
        with allure.step("验证响应状态码"):
            assert response.status_code == 401
        
        with allure.step("验证错误信息"):
            data = response.json()
            assert "detail" in data
    
    @allure.story("用户注册")
    @pytest.mark.api
    def test_register_success(self, test_client: TestClient):
        """测试用户成功注册"""
        with allure.step("发送注册请求"):
            response = test_client.post("/api/v1/auth/register", json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "newpassword"
            })
        
        with allure.step("验证响应状态码"):
            assert response.status_code == 200
        
        with allure.step("验证响应内容"):
            data = response.json()
            assert data["username"] == "newuser"
            assert data["email"] == "newuser@example.com"
    
    @allure.story("获取用户信息")
    @pytest.mark.api
    def test_get_current_user(self, test_client: TestClient, auth_headers):
        """测试获取当前用户信息"""
        with allure.step("发送获取用户信息请求"):
            response = test_client.get("/api/v1/auth/me", headers=auth_headers)
        
        with allure.step("验证响应状态码"):
            assert response.status_code == 200
        
        with allure.step("验证响应内容"):
            data = response.json()
            assert "id" in data
            assert "username" in data
            assert "email" in data
