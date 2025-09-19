import pytest
import allure
from playwright.async_api import Page

@allure.feature("登录页面")
class TestLoginPage:
    
    @allure.story("页面加载")
    @pytest.mark.ui
    async def test_login_page_loads(self, page: Page):
        """测试登录页面加载"""
        with allure.step("访问登录页面"):
            await page.goto("http://localhost:3000/login")
        
        with allure.step("验证页面标题"):
            title = await page.title()
            assert "自动化测试平台" in title
        
        with allure.step("验证登录表单存在"):
            await page.wait_for_selector('input[placeholder="用户名"]')
            await page.wait_for_selector('input[placeholder="密码"]')
            await page.wait_for_selector('button[type="submit"]')
    
    @allure.story("用户登录")
    @pytest.mark.ui
    async def test_login_success(self, page: Page):
        """测试用户成功登录"""
        with allure.step("访问登录页面"):
            await page.goto("http://localhost:3000/login")
        
        with allure.step("输入用户名"):
            await page.fill('input[placeholder="用户名"]', "testuser")
        
        with allure.step("输入密码"):
            await page.fill('input[placeholder="密码"]', "testpassword")
        
        with allure.step("点击登录按钮"):
            await page.click('button[type="submit"]')
        
        with allure.step("验证跳转到仪表板"):
            await page.wait_for_url("http://localhost:3000/dashboard", timeout=5000)
            assert "dashboard" in page.url
        
        with allure.step("截图保存"):
            await page.screenshot(path="login_success.png")
            allure.attach.file("login_success.png", attachment_type=allure.attachment_type.PNG)
    
    @allure.story("用户登录")
    @pytest.mark.ui
    async def test_login_invalid_credentials(self, page: Page):
        """测试无效凭据登录"""
        with allure.step("访问登录页面"):
            await page.goto("http://localhost:3000/login")
        
        with allure.step("输入无效用户名"):
            await page.fill('input[placeholder="用户名"]', "invaliduser")
        
        with allure.step("输入无效密码"):
            await page.fill('input[placeholder="密码"]', "invalidpassword")
        
        with allure.step("点击登录按钮"):
            await page.click('button[type="submit"]')
        
        with allure.step("验证显示错误信息"):
            # 等待错误消息显示
            await page.wait_for_selector('.ant-message-error', timeout=5000)
        
        with allure.step("验证仍在登录页面"):
            assert "login" in page.url
    
    @allure.story("用户注册")
    @pytest.mark.ui
    async def test_register_tab_switch(self, page: Page):
        """测试切换到注册标签"""
        with allure.step("访问登录页面"):
            await page.goto("http://localhost:3000/login")
        
        with allure.step("点击注册标签"):
            await page.click('div[role="tab"]:has-text("注册")')
        
        with allure.step("验证注册表单显示"):
            await page.wait_for_selector('input[placeholder="邮箱"]')
            await page.wait_for_selector('input[placeholder="确认密码"]')
        
        with allure.step("截图保存"):
            await page.screenshot(path="register_form.png")
            allure.attach.file("register_form.png", attachment_type=allure.attachment_type.PNG)
