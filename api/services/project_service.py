"""Business logic for the project creation feature."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client

from models.project import (
    Project,
    ProjectCreate,
    ProjectFilter,
    ProjectStatus,
    ProjectUpdate,
)
from models.user import User
from services.supabase import supabase_service


class ProjectService:
    """Encapsulates project specific data access and validation logic."""

    def __init__(self, supabase: Optional[Client] = None) -> None:
        """Create a ProjectService instance backed by a Supabase client."""
        self.supabase = supabase or supabase_service.client


    async def create_project(self, payload: ProjectCreate, current_user: User) -> Project:
        """Create a new project after verifying permissions and inputs."""
        self._ensure_creator_permissions(current_user)

        property_record = self._fetch_property(payload.property_id)
        self._verify_property_access(property_record, current_user)

        project_dict = self._build_project_insert_dict(payload, current_user)

        result = self.supabase.table("projects").insert(project_dict).execute()
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create project",
            )

        return Project(**result.data[0])

    async def get_project(self, project_id: UUID, current_user: User) -> Project:
        """Retrieve a single project ensuring the requester has access."""
        result = (
            self.supabase.table("projects")
            .select("*")
            .eq("id", str(project_id))
            .limit(1)
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        project_record = result.data[0]
        property_record = self._fetch_property(UUID(project_record["property_id"]))
        self._verify_property_access(property_record, current_user)

        return Project(**project_record)

    async def list_projects(
        self,
        filters: ProjectFilter,
        current_user: User,
        page: int = 1,
        per_page: int = 20,
    ) -> Tuple[List[Project], int]:
        """Return projects visible to the current user with pagination."""
        property_ids = self._get_accessible_property_ids(current_user)
        if not property_ids:
            return [], 0

        query = self.supabase.table("projects").select("*", count="exact")
        query = query.in_("property_id", property_ids)

        if filters.status:
            query = query.eq("status", filters.status.value)
        if filters.category:
            query = query.eq("category", filters.category.value)
        if filters.urgency:
            query = query.eq("urgency", filters.urgency.value)
        if filters.property_id:
            if str(filters.property_id) not in property_ids:
                return [], 0
            query = query.eq("property_id", str(filters.property_id))
        if filters.search:
            like = f"%{filters.search}%"
            query = query.or_(
                f"title.ilike.{like},description.ilike.{like}"
            )

        offset = (page - 1) * per_page
        query = query.range(offset, offset + per_page - 1)
        query = query.order("created_at", desc=True)

        result = query.execute()

        projects = [Project(**record) for record in result.data]
        total = result.count or 0

        return projects, total

    async def update_project(
        self,
        project_id: UUID,
        payload: ProjectUpdate,
        current_user: User,
    ) -> Project:
        """Update a project when the user has permission."""
        existing = await self.get_project(project_id, current_user)
        update_payload = self._build_project_update_dict(payload)

        if not update_payload:
            return existing

        result = (
            self.supabase.table("projects")
            .update(update_payload)
            .eq("id", str(project_id))
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update project",
            )

        return Project(**result.data[0])

    async def update_status(
        self,
        project_id: UUID,
        status_update: ProjectStatus,
        current_user: User,
    ) -> Project:
        """Update a project's lifecycle status."""
        await self.get_project(project_id, current_user)

        update_dict: Dict[str, object] = {
            "status": status_update.value,
            "updated_at": datetime.utcnow().isoformat(),
        }

        if status_update == ProjectStatus.OPEN_FOR_BIDS:
            update_dict["published_at"] = datetime.utcnow().isoformat()
        if status_update in {ProjectStatus.BIDDING_CLOSED, ProjectStatus.CANCELLED}:
            update_dict["closed_at"] = datetime.utcnow().isoformat()

        result = (
            self.supabase.table("projects")
            .update(update_dict)
            .eq("id", str(project_id))
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update project status",
            )

        return Project(**result.data[0])

    async def delete_project(self, project_id: UUID, current_user: User) -> None:
        """Delete a project that is still in draft form."""
        project = await self.get_project(project_id, current_user)
        if project.status != ProjectStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only draft projects can be deleted",
            )

        result = (
            self.supabase.table("projects")
            .delete()
            .eq("id", str(project_id))
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete project",
            )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _ensure_creator_permissions(self, current_user: User) -> None:
        if current_user.role not in {"admin", "manager"}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins or managers can create projects",
            )

    def _fetch_property(self, property_id: UUID) -> Dict[str, object]:
        result = (
            self.supabase.table("properties")
            .select("id, organization_id, manager_id")
            .eq("id", str(property_id))
            .limit(1)
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found",
            )

        return result.data[0]

    def _verify_property_access(
        self, property_record: Dict[str, object], current_user: User
    ) -> None:
        organization_id = property_record.get("organization_id")
        manager_id = property_record.get("manager_id")

        if current_user.organization_id and organization_id:
            if str(current_user.organization_id) != organization_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You cannot modify projects for another organization",
                )

        if current_user.role == "manager" and manager_id and manager_id != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Managers can only manage their assigned properties",
            )

    def _build_project_insert_dict(
        self, payload: ProjectCreate, current_user: User
    ) -> Dict[str, object]:
        now_iso = datetime.utcnow().isoformat()
        status_value = payload.status.value

        if payload.publish:
            status_value = ProjectStatus.OPEN_FOR_BIDS.value

        project_dict: Dict[str, object] = {
            "property_id": str(payload.property_id),
            "created_by": str(current_user.id),
            "title": payload.title,
            "description": payload.description,
            "category": payload.category.value,
            "urgency": payload.urgency.value,
            "bid_deadline": payload.bid_deadline.isoformat(),
            "preferred_start_date": payload.preferred_start_date.isoformat()
            if payload.preferred_start_date
            else None,
            "completion_deadline": payload.completion_deadline.isoformat()
            if payload.completion_deadline
            else None,
            "budget_min": payload.budget_min,
            "budget_max": payload.budget_max,
            "budget_range": payload.budget_range.value if payload.budget_range else None,
            "insurance_required": payload.insurance_required,
            "license_required": payload.license_required,
            "minimum_bids": payload.minimum_bids,
            "is_open_bidding": payload.is_open_bidding,
            "virtual_access": payload.virtual_access.dict(exclude_none=True)
            if payload.virtual_access
            else None,
            "location_details": payload.location_details,
            "special_conditions": payload.special_conditions,
            "status": status_value,
            "updated_at": now_iso,
        }

        if payload.publish:
            project_dict["published_at"] = now_iso

        return project_dict

    def _build_project_update_dict(self, payload: ProjectUpdate) -> Dict[str, object]:
        update_dict: Dict[str, object] = {}
        data = payload.dict(exclude_unset=True)

        for key, value in data.items():
            if value is None:
                update_dict[key] = None
                continue

            if key in {"category", "urgency", "status"}:
                update_dict[key] = value.value  # Enum to str
            elif key in {"bid_deadline"}:
                update_dict[key] = value.isoformat()
            elif key in {"preferred_start_date", "completion_deadline"}:
                update_dict[key] = value.isoformat() if value else None
            elif key == "budget_range":
                update_dict[key] = value.value
            elif key == "virtual_access":
                update_dict[key] = value.dict(exclude_none=True)
            else:
                update_dict[key] = value

        if update_dict:
            update_dict["updated_at"] = datetime.utcnow().isoformat()

        return update_dict

    def _get_accessible_property_ids(self, current_user: User) -> List[str]:
        if not current_user.organization_id:
            return []

        query = (
            self.supabase.table("properties")
            .select("id")
            .eq("organization_id", str(current_user.organization_id))
            .eq("deleted_at", None)
        )

        if current_user.role == "manager":
            query = query.eq("manager_id", str(current_user.id))

        result = query.execute()
        return [record["id"] for record in result.data]


__all__ = ["ProjectService"]
