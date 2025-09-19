from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from core.security import get_current_active_user
from models.user import User
from models.project import Project
from models.test_execution import TestExecution
from models.environment import Environment
from schemas.test_execution import (
    TestExecution as TestExecutionSchema, 
    TestExecutionCreate, 
    TestExecutionUpdate
)
from services.test_service import TestExecutionService

router = APIRouter()
test_service = TestExecutionService()

@router.get("/projects/{project_id}/executions", response_model=List[TestExecutionSchema])
async def get_executions(
    project_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取测试执行历史"""
    # 检查项目权限
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if current_user.role != "admin" and project.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    executions = db.query(TestExecution).filter(
        TestExecution.project_id == project_id
    ).order_by(TestExecution.created_at.desc()).offset(skip).limit(limit).all()
    
    return executions

@router.get("/executions/{execution_id}", response_model=TestExecutionSchema)
async def get_execution(
    execution_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取测试执行详情"""
    execution = db.query(TestExecution).filter(TestExecution.id == execution_id).first()
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    # 检查项目权限
    project = db.query(Project).filter(Project.id == execution.project_id).first()
    if current_user.role != "admin" and project.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return execution

@router.post("/projects/{project_id}/execute", response_model=TestExecutionSchema)
async def execute_tests(
    project_id: int,
    execution_data: TestExecutionCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """执行测试"""
    # 检查项目权限
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if current_user.role != "admin" and project.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # 检查环境是否存在
    environment = db.query(Environment).filter(
        Environment.id == execution_data.environment_id,
        Environment.project_id == project_id
    ).first()
    
    if not environment:
        raise HTTPException(status_code=404, detail="Environment not found")
    
    # 创建执行记录
    db_execution = TestExecution(
        project_id=project_id,
        environment_id=execution_data.environment_id,
        status="pending",
        created_by=current_user.id
    )
    db.add(db_execution)
    db.commit()
    db.refresh(db_execution)
    
    # 后台执行测试
    background_tasks.add_task(
        test_service.run_tests,
        db_execution.id,
        execution_data.test_case_ids
    )
    
    return db_execution

@router.post("/executions/{execution_id}/stop")
async def stop_execution(
    execution_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """停止测试执行"""
    execution = db.query(TestExecution).filter(TestExecution.id == execution_id).first()
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    # 检查项目权限
    project = db.query(Project).filter(Project.id == execution.project_id).first()
    if current_user.role != "admin" and project.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    if execution.status == "running":
        await test_service.stop_execution(execution_id)
        execution.status = "failed"
        execution.result = {"message": "Execution stopped by user"}
        db.commit()
    
    return {"message": "Execution stopped successfully"}
