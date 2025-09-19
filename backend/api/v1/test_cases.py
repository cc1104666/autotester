from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from core.security import get_current_active_user
from models.user import User
from models.project import Project
from models.test_case import TestCase
from schemas.test_case import TestCase as TestCaseSchema, TestCaseCreate, TestCaseUpdate

router = APIRouter()

@router.get("/projects/{project_id}/test-cases", response_model=List[TestCaseSchema])
async def get_test_cases(
    project_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    test_type: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取测试用例列表"""
    # 检查项目权限
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if current_user.role != "admin" and project.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    query = db.query(TestCase).filter(TestCase.project_id == project_id)
    
    if test_type:
        query = query.filter(TestCase.type == test_type)
    
    test_cases = query.offset(skip).limit(limit).all()
    return test_cases

@router.get("/test-cases/{case_id}", response_model=TestCaseSchema)
async def get_test_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取测试用例详情"""
    test_case = db.query(TestCase).filter(TestCase.id == case_id).first()
    
    if not test_case:
        raise HTTPException(status_code=404, detail="Test case not found")
    
    # 检查项目权限
    project = db.query(Project).filter(Project.id == test_case.project_id).first()
    if current_user.role != "admin" and project.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return test_case

@router.post("/projects/{project_id}/test-cases", response_model=TestCaseSchema)
async def create_test_case(
    project_id: int,
    test_case: TestCaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建测试用例"""
    # 检查项目权限
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if current_user.role != "admin" and project.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_test_case = TestCase(
        **test_case.dict(),
        project_id=project_id,
        created_by=current_user.id
    )
    db.add(db_test_case)
    db.commit()
    db.refresh(db_test_case)
    
    return db_test_case

@router.put("/test-cases/{case_id}", response_model=TestCaseSchema)
async def update_test_case(
    case_id: int,
    test_case_update: TestCaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新测试用例"""
    test_case = db.query(TestCase).filter(TestCase.id == case_id).first()
    
    if not test_case:
        raise HTTPException(status_code=404, detail="Test case not found")
    
    # 检查项目权限
    project = db.query(Project).filter(Project.id == test_case.project_id).first()
    if current_user.role != "admin" and project.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # 更新字段
    update_data = test_case_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(test_case, field, value)
    
    db.commit()
    db.refresh(test_case)
    
    return test_case

@router.delete("/test-cases/{case_id}")
async def delete_test_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除测试用例"""
    test_case = db.query(TestCase).filter(TestCase.id == case_id).first()
    
    if not test_case:
        raise HTTPException(status_code=404, detail="Test case not found")
    
    # 检查项目权限
    project = db.query(Project).filter(Project.id == test_case.project_id).first()
    if current_user.role != "admin" and project.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db.delete(test_case)
    db.commit()
    
    return {"message": "Test case deleted successfully"}
