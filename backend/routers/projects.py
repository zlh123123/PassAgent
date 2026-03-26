"""兼容性 projects 路由。

某些本地工具或旧前端会探测 `/api/projects`。
当前主工程没有项目(Project)资源，因此这里返回空列表，
避免持续产生 404 噪音日志。
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("")
def list_projects():
    return {"projects": []}
