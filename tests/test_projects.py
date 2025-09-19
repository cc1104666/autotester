import pytest
import allure
from fastapi.testclient import TestClient

@allure.feature("项目管理")
class TestProjects:
    
    @allure.story("创建项目")
    @pytest.mark.api
    def test_create_project(self, test_client: TestClient, auth_headers):
        """测试创建项目"""
        project_data = {
            "name": "测试项目",
            "description": "这是一个测试项目",
            "repository_url": "https://github.com/test/project.git"
        }
        
        with allure.step("发送创建项目请求"):
            response = test_client.post(
                "/api/v1/projects",
                json=project_data,
                headers=auth_headers
            )
        
        with allure.step("验证响应状态码"):
            assert response.status_code == 200
        
        with allure.step("验证响应内容"):
            data = response.json()
            assert data["name"] == project_data["name"]
            assert data["description"] == project_data["description"]
            assert data["repository_url"] == project_data["repository_url"]
            assert "id" in data
            assert "created_at" in data
    
    @allure.story("获取项目列表")
    @pytest.mark.api
    def test_get_projects(self, test_client: TestClient, auth_headers):
        """测试获取项目列表"""
        with allure.step("发送获取项目列表请求"):
            response = test_client.get("/api/v1/projects", headers=auth_headers)
        
        with allure.step("验证响应状态码"):
            assert response.status_code == 200
        
        with allure.step("验证响应内容"):
            data = response.json()
            assert isinstance(data, list)
    
    @allure.story("获取项目详情")
    @pytest.mark.api
    def test_get_project_detail(self, test_client: TestClient, auth_headers):
        """测试获取项目详情"""
        # 先创建一个项目
        project_data = {
            "name": "详情测试项目",
            "description": "用于测试获取详情的项目"
        }
        
        create_response = test_client.post(
            "/api/v1/projects",
            json=project_data,
            headers=auth_headers
        )
        project_id = create_response.json()["id"]
        
        with allure.step("发送获取项目详情请求"):
            response = test_client.get(
                f"/api/v1/projects/{project_id}",
                headers=auth_headers
            )
        
        with allure.step("验证响应状态码"):
            assert response.status_code == 200
        
        with allure.step("验证响应内容"):
            data = response.json()
            assert data["name"] == project_data["name"]
            assert data["description"] == project_data["description"]
    
    @allure.story("更新项目")
    @pytest.mark.api
    def test_update_project(self, test_client: TestClient, auth_headers):
        """测试更新项目"""
        # 先创建一个项目
        project_data = {
            "name": "更新测试项目",
            "description": "用于测试更新的项目"
        }
        
        create_response = test_client.post(
            "/api/v1/projects",
            json=project_data,
            headers=auth_headers
        )
        project_id = create_response.json()["id"]
        
        # 更新项目
        update_data = {
            "name": "已更新的项目名称",
            "description": "已更新的项目描述"
        }
        
        with allure.step("发送更新项目请求"):
            response = test_client.put(
                f"/api/v1/projects/{project_id}",
                json=update_data,
                headers=auth_headers
            )
        
        with allure.step("验证响应状态码"):
            assert response.status_code == 200
        
        with allure.step("验证响应内容"):
            data = response.json()
            assert data["name"] == update_data["name"]
            assert data["description"] == update_data["description"]
    
    @allure.story("删除项目")
    @pytest.mark.api
    def test_delete_project(self, test_client: TestClient, admin_auth_headers):
        """测试删除项目"""
        # 先创建一个项目
        project_data = {
            "name": "删除测试项目",
            "description": "用于测试删除的项目"
        }
        
        create_response = test_client.post(
            "/api/v1/projects",
            json=project_data,
            headers=admin_auth_headers
        )
        project_id = create_response.json()["id"]
        
        with allure.step("发送删除项目请求"):
            response = test_client.delete(
                f"/api/v1/projects/{project_id}",
                headers=admin_auth_headers
            )
        
        with allure.step("验证响应状态码"):
            assert response.status_code == 200
        
        with allure.step("验证项目已被删除"):
            get_response = test_client.get(
                f"/api/v1/projects/{project_id}",
                headers=admin_auth_headers
            )
            assert get_response.status_code == 404
