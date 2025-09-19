import asyncio
import subprocess
import json
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import pytest
from playwright.async_api import async_playwright

from core.database import SessionLocal
from models.test_execution import TestExecution
from models.test_case import TestCase
from models.environment import Environment
from models.project import Project
from utils.allure_utils import generate_allure_report

class TestExecutionService:
    """测试执行服务"""
    
    def __init__(self):
        self.running_executions = {}
    
    async def run_tests(self, execution_id: int, test_case_ids: Optional[List[int]] = None):
        """运行测试"""
        db = SessionLocal()
        try:
            execution = db.query(TestExecution).filter(TestExecution.id == execution_id).first()
            if not execution:
                return
            
            # 更新状态为运行中
            execution.status = "running"
            execution.start_time = datetime.utcnow()
            db.commit()
            
            # 获取测试用例
            test_cases_query = db.query(TestCase).filter(TestCase.project_id == execution.project_id)
            if test_case_ids:
                test_cases_query = test_cases_query.filter(TestCase.id.in_(test_case_ids))
            
            test_cases = test_cases_query.all()
            
            # 获取环境信息
            environment = db.query(Environment).filter(Environment.id == execution.environment_id).first()
            
            # 分类测试用例
            api_cases = [tc for tc in test_cases if tc.type == "api"]
            ui_cases = [tc for tc in test_cases if tc.type == "ui"]
            
            results = {
                "api_results": [],
                "ui_results": [],
                "summary": {}
            }
            
            # 执行API测试
            if api_cases:
                api_results = await self.execute_api_tests(execution_id, api_cases, environment)
                results["api_results"] = api_results
            
            # 执行UI测试
            if ui_cases:
                ui_results = await self.execute_ui_tests(execution_id, ui_cases, environment)
                results["ui_results"] = ui_results
            
            # 生成测试报告
            report_path = await self.generate_test_report(execution_id)
            
            # 计算总结果
            all_passed = all(
                result.get("status") == "passed" 
                for result in results["api_results"] + results["ui_results"]
            )
            
            # 更新执行结果
            execution.status = "passed" if all_passed else "failed"
            execution.end_time = datetime.utcnow()
            execution.result = results
            execution.report_path = report_path
            db.commit()
            
        except Exception as e:
            # 错误处理
            execution.status = "failed"
            execution.end_time = datetime.utcnow()
            execution.result = {"error": str(e)}
            db.commit()
        finally:
            db.close()
            # 清理运行状态
            self.running_executions.pop(execution_id, None)
    
    async def execute_api_tests(self, execution_id: int, test_cases: List[TestCase], environment: Environment) -> List[Dict[str, Any]]:
        """执行API测试"""
        results = []
        
        for test_case in test_cases:
            try:
                # 生成pytest测试文件
                test_file = self._generate_api_test_file(test_case, environment)
                
                # 执行pytest
                result = subprocess.run([
                    "pytest",
                    str(test_file),
                    "--allure-dir=./allure-results",
                    "--json-report",
                    f"--json-report-file=./test-report-{test_case.id}.json",
                    "-v"
                ], capture_output=True, text=True, cwd="./")
                
                # 解析结果
                test_result = {
                    "test_case_id": test_case.id,
                    "test_case_name": test_case.name,
                    "status": "passed" if result.returncode == 0 else "failed",
                    "output": result.stdout,
                    "errors": result.stderr,
                    "duration": 0  # 可以从JSON报告中提取
                }
                
                # 尝试读取JSON报告获取详细信息
                try:
                    with open(f"./test-report-{test_case.id}.json", "r") as f:
                        json_report = json.load(f)
                        test_result["duration"] = json_report.get("duration", 0)
                        test_result["details"] = json_report
                except:
                    pass
                
                results.append(test_result)
                
            except Exception as e:
                results.append({
                    "test_case_id": test_case.id,
                    "test_case_name": test_case.name,
                    "status": "error",
                    "error": str(e)
                })
        
        return results
    
    async def execute_ui_tests(self, execution_id: int, test_cases: List[TestCase], environment: Environment) -> List[Dict[str, Any]]:
        """执行UI测试"""
        results = []
        
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            context = await browser.new_context()
            
            for test_case in test_cases:
                page = await context.new_page()
                try:
                    start_time = datetime.utcnow()
                    
                    # 执行UI测试步骤
                    result = await self._execute_ui_steps(page, test_case, environment)
                    
                    end_time = datetime.utcnow()
                    duration = (end_time - start_time).total_seconds()
                    
                    results.append({
                        "test_case_id": test_case.id,
                        "test_case_name": test_case.name,
                        "status": result.get("status", "failed"),
                        "details": result,
                        "duration": duration
                    })
                    
                except Exception as e:
                    results.append({
                        "test_case_id": test_case.id,
                        "test_case_name": test_case.name,
                        "status": "error",
                        "error": str(e)
                    })
                finally:
                    await page.close()
            
            await browser.close()
        
        return results
    
    def _generate_api_test_file(self, test_case: TestCase, environment: Environment) -> Path:
        """生成API测试文件"""
        test_data = test_case.test_data or {}
        base_url = environment.base_url or "http://localhost:8000"
        
        # 生成pytest测试代码
        test_code = f"""
import pytest
import requests
import allure

@allure.feature("{test_case.project.name if hasattr(test_case, 'project') else 'API Test'}")
@allure.story("{test_case.name}")
def test_{test_case.id}():
    \"\"\"自动生成的API测试: {test_case.name}\"\"\"
    
    base_url = "{base_url}"
    test_data = {json.dumps(test_data, indent=4)}
    
    # 执行HTTP请求
    method = test_data.get("method", "GET").upper()
    endpoint = test_data.get("endpoint", "/")
    headers = test_data.get("headers", {{}})
    params = test_data.get("params", {{}})
    json_data = test_data.get("json", None)
    
    url = base_url + endpoint
    
    with allure.step(f"发送{{method}}请求到{{url}}"):
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, params=params, json=json_data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, params=params, json=json_data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, params=params)
        else:
            raise ValueError(f"Unsupported HTTP method: {{method}}")
    
    # 验证响应
    expected_status = test_data.get("expected_status", 200)
    with allure.step(f"验证状态码为{{expected_status}}"):
        assert response.status_code == expected_status, f"Expected {{expected_status}}, got {{response.status_code}}"
    
    # 验证响应内容
    if "expected_response" in test_data:
        with allure.step("验证响应内容"):
            expected = test_data["expected_response"]
            actual = response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
            assert expected == actual, f"Expected {{expected}}, got {{actual}}"
"""
        
        # 写入临时文件
        test_file = Path(f"./temp_test_{test_case.id}_{uuid.uuid4().hex[:8]}.py")
        test_file.write_text(test_code)
        
        return test_file
    
    async def _execute_ui_steps(self, page, test_case: TestCase, environment: Environment) -> Dict[str, Any]:
        """执行UI测试步骤"""
        test_data = test_case.test_data or {}
        base_url = environment.base_url or "http://localhost:3000"
        
        steps = test_data.get("steps", [])
        
        try:
            for i, step in enumerate(steps):
                action = step.get("action")
                selector = step.get("selector")
                value = step.get("value")
                expected = step.get("expected")
                
                if action == "goto":
                    url = base_url + (value or "/")
                    await page.goto(url)
                
                elif action == "fill":
                    await page.fill(selector, value)
                
                elif action == "click":
                    await page.click(selector)
                
                elif action == "wait":
                    timeout = int(value or 5000)
                    await page.wait_for_timeout(timeout)
                
                elif action == "wait_for_selector":
                    timeout = int(value or 30000)
                    await page.wait_for_selector(selector, timeout=timeout)
                
                elif action == "assert_text":
                    element = await page.wait_for_selector(selector)
                    text = await element.text_content()
                    assert expected in text, f"Expected '{expected}' in '{text}'"
                
                elif action == "assert_url":
                    current_url = page.url
                    assert expected in current_url, f"Expected '{expected}' in '{current_url}'"
                
                elif action == "screenshot":
                    screenshot_path = f"./screenshots/step_{i}_{uuid.uuid4().hex[:8]}.png"
                    await page.screenshot(path=screenshot_path)
            
            return {"status": "passed", "message": "All steps completed successfully"}
            
        except Exception as e:
            # 截图保存错误状态
            error_screenshot = f"./screenshots/error_{uuid.uuid4().hex[:8]}.png"
            await page.screenshot(path=error_screenshot)
            
            return {
                "status": "failed",
                "error": str(e),
                "screenshot": error_screenshot
            }
    
    async def generate_test_report(self, execution_id: int) -> str:
        """生成测试报告"""
        try:
            report_path = f"./allure-reports/execution-{execution_id}"
            
            # 生成Allure报告
            result = subprocess.run([
                "allure", "generate",
                "./allure-results",
                "-o", report_path,
                "--clean"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return report_path
            else:
                return None
                
        except Exception as e:
            print(f"Error generating report: {e}")
            return None
    
    async def stop_execution(self, execution_id: int):
        """停止测试执行"""
        if execution_id in self.running_executions:
            # 这里可以实现停止逻辑，比如杀死进程等
            self.running_executions[execution_id]["stopped"] = True
