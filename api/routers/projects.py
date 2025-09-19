"""Project creation and management API endpoints."""

from typing import Optional
from uuid import UUID

from dependencies import get_current_user
from fastapi import APIRouter, Depends, Query, status
from models.project import (
    Project,
    ProjectCreate,
    ProjectFilter,
    ProjectListResponse,
    ProjectStatusUpdate,
    ProjectUpdate,
)
from models.user import User
from services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(lambda: ProjectService()),
) -> Project:
    """Create a new maintenance project."""
    return await service.create_project(project_data, current_user)


@router.get("/", response_model=ProjectListResponse)
async def list_projects(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, max_length=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    category: Optional[str] = None,
    urgency: Optional[str] = None,
    property_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(lambda: ProjectService()),
) -> ProjectListResponse:
    """List projects visible to the authenticated user."""
    filters = ProjectFilter(
        search=search,
        status=status_filter,
        category=category,
        urgency=urgency,
        property_id=property_id,
    )

    projects, total = await service.list_projects(
        filters=filters,
        current_user=current_user,
        page=page,
        per_page=per_page,
    )

    return ProjectListResponse(
        projects=projects,
        total=total,
        page=page,
        per_page=per_page,
        has_next=page * per_page < total,
        has_prev=page > 1,
    )


@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(lambda: ProjectService()),
) -> Project:
    """Retrieve a single project by ID."""
    return await service.get_project(project_id, current_user)


@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: UUID,
    update_payload: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(lambda: ProjectService()),
) -> Project:
    """Update an existing project."""
    return await service.update_project(project_id, update_payload, current_user)


@router.patch("/{project_id}/status", response_model=Project)
async def update_project_status(
    project_id: UUID,
    status_payload: ProjectStatusUpdate,
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(lambda: ProjectService()),
) -> Project:
    """Transition a project to a new lifecycle status."""
    return await service.update_status(project_id, status_payload.status, current_user)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(lambda: ProjectService()),
) -> None:
    """Delete a draft project."""
    await service.delete_project(project_id, current_user)


__all__ = ["router"]
