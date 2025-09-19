import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional

def generate_allure_report(results_dir: str, output_dir: str) -> Optional[str]:
    """生成Allure报告"""
    try:
        # 确保目录存在
        Path(results_dir).mkdir(parents=True, exist_ok=True)
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # 生成Allure报告
        result = subprocess.run([
            "allure", "generate",
            results_dir,
            "-o", output_dir,
            "--clean"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            return output_dir
        else:
            print(f"Allure generation failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"Error generating Allure report: {e}")
        return None

def parse_allure_results(results_dir: str) -> Dict[str, Any]:
    """解析Allure结果"""
    results_path = Path(results_dir)
    summary = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "broken": 0,
        "skipped": 0,
        "tests": []
    }
    
    try:
        # 读取测试结果文件
        for result_file in results_path.glob("*-result.json"):
            with open(result_file, 'r', encoding='utf-8') as f:
                test_result = json.load(f)
                
                summary["total"] += 1
                status = test_result.get("status", "unknown")
                
                if status == "passed":
                    summary["passed"] += 1
                elif status == "failed":
                    summary["failed"] += 1
                elif status == "broken":
                    summary["broken"] += 1
                elif status == "skipped":
                    summary["skipped"] += 1
                
                summary["tests"].append({
                    "name": test_result.get("name", "Unknown"),
                    "status": status,
                    "duration": test_result.get("stop", 0) - test_result.get("start", 0),
                    "uuid": test_result.get("uuid")
                })
    
    except Exception as e:
        print(f"Error parsing Allure results: {e}")
    
    return summary

def create_allure_environment_properties(environment_config: Dict[str, Any]) -> str:
    """创建Allure环境配置文件"""
    properties = []
    
    for key, value in environment_config.items():
        properties.append(f"{key}={value}")
    
    return "\n".join(properties)
