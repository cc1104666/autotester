# 导入所有模型以便自动创建表
from .user import User
from .project import Project
from .environment import Environment
from .test_case import TestCase
from .test_execution import TestExecution

__all__ = ["User", "Project", "Environment", "TestCase", "TestExecution"]
