# backend/app/api/v1/routes/projects.py
"""Project management routes with multi-tenant isolation"""

from typing import List
from fastapi import APIRouter, HTTPException, status, Depends, Query

from app.services.project_service import ProjectService
from app.models import ProjectCreate, ProjectResponse, User
from app.middleware import get_current_active_user

router = APIRouter(prefix="/projects", tags=["projects"])


def _get_tenant(user: User) -> str:
    """Extract tenant_id with fallback to user.id"""
    return getattr(user, "tenant_id", None) or str(user.id)


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new project scoped to the current tenant
    """
    project_service = ProjectService()
    tenant_id = _get_tenant(current_user)
    project = await project_service.create_project(
        user_id=str(current_user.id),
        project_data=project_data,
        tenant_id=tenant_id
    )
    
    return ProjectResponse(
        _id=str(project.id),
        user_id=str(project.user_id),
        tenant_id=project.tenant_id,
        name=project.name,
        description=project.description,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user)
):
    """
    List tenant's projects with pagination
    """
    project_service = ProjectService()
    tenant_id = _get_tenant(current_user)
    projects = await project_service.get_user_projects(
        user_id=str(current_user.id),
        skip=skip,
        limit=limit,
        tenant_id=tenant_id
    )
    
    return [
        ProjectResponse(
            _id=str(p.id),
            user_id=str(p.user_id),
            tenant_id=p.tenant_id,
            name=p.name,
            description=p.description,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
        for p in projects
    ]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific project with tenant ownership verification
    """
    project_service = ProjectService()
    tenant_id = _get_tenant(current_user)
    project = await project_service.get_project(
        project_id=project_id,
        user_id=str(current_user.id),
        tenant_id=tenant_id
    )
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or access denied"
        )
    
    return ProjectResponse(
        _id=str(project.id),
        user_id=str(project.user_id),
        tenant_id=project.tenant_id,
        name=project.name,
        description=project.description,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a project and all associated videos with tenant verification
    """
    project_service = ProjectService()
    tenant_id = _get_tenant(current_user)
    deleted = await project_service.delete_project(
        project_id=project_id,
        user_id=str(current_user.id),
        tenant_id=tenant_id
    )
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or access denied"
        )


@router.get("/{project_id}/history")
async def get_project_history(
    project_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get video generation history for a project with tenant verification
    """
    project_service = ProjectService()
    tenant_id = _get_tenant(current_user)
    videos = await project_service.get_project_history(
        project_id=project_id,
        user_id=str(current_user.id),
        tenant_id=tenant_id
    )
    
    return {"videos": videos}
