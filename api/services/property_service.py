"""Property service for business logic and database operations."""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

import httpx
from fastapi import HTTPException, status
from models.property import (
    Property,
    PropertyBulkCreate,
    PropertyCoordinates,
    PropertyCreate,
    PropertyExport,
    PropertyFilter,
    PropertyGroup,
    PropertyGroupCreate,
    PropertyGroupUpdate,
    PropertyImport,
    PropertyStatus,
    PropertyType,
    PropertyUpdate,
)
from services.supabase import supabase_service
from supabase import Client

logger = logging.getLogger(__name__)


class PropertyService:
    """Service for managing properties."""

    def __init__(self, supabase: Client = None):
        """Initialize property service."""
        self.supabase = supabase or supabase_service.client
        self.geocoding_api_key = None  # Set from environment

    async def create_property(self, data: PropertyCreate, user_id: UUID) -> Property:
        """Create a new property."""
        try:
            # Check for duplicate address
            existing = (
                self.supabase.table("properties")
                .select("id")
                .eq("organization_id", str(data.organization_id))
                .eq("address", data.address)
                .eq("deleted_at", None)
                .execute()
            )

            if existing.data:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Property with this address already exists",
                )

            # Geocode address if coordinates not provided
            if not data.coordinates:
                coords = await self._geocode_address(
                    f"{data.address}, {data.city}, {data.state} {data.zip}"
                )
                if coords:
                    data.coordinates = coords

            # Prepare property data
            property_dict = data.dict(exclude_unset=True)

            # Convert coordinates to PostGIS point
            if data.coordinates:
                property_dict["coordinates"] = (
                    f"POINT({data.coordinates.longitude} {data.coordinates.latitude})"
                )

            # Convert Pydantic models to dicts
            if "details" in property_dict:
                property_dict["details"] = property_dict["details"].dict(
                    exclude_none=True
                )
            if "photos" in property_dict:
                property_dict["photos"] = [
                    photo.dict() for photo in property_dict["photos"]
                ]

            # Create property
            result = self.supabase.table("properties").insert(property_dict).execute()

            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create property",
                )

            # Log audit
            await self._log_audit(
                property_id=result.data[0]["id"],
                action="created",
                changes=property_dict,
                user_id=user_id,
            )

            return Property(**result.data[0])

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating property: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create property: {str(e)}",
            )

    async def get_properties(
        self, filters: PropertyFilter, user_id: UUID, page: int = 1, per_page: int = 20
    ) -> Tuple[List[Property], int]:
        """Get filtered list of properties."""
        try:
            query = self.supabase.table("properties").select("*", count="exact")

            # Apply filters
            if not filters.include_archived:
                query = query.eq("deleted_at", None)

            if filters.search:
                query = query.or_(
                    f"name.ilike.%{filters.search}%,"
                    f"address.ilike.%{filters.search}%,"
                    f"city.ilike.%{filters.search}%"
                )

            if filters.property_type:
                query = query.eq("property_type", filters.property_type.value)

            if filters.status:
                query = query.eq("status", filters.status.value)

            if filters.manager_id:
                query = query.eq("manager_id", str(filters.manager_id))

            if filters.city:
                query = query.eq("city", filters.city)

            if filters.state:
                query = query.eq("state", filters.state)

            # Apply JSONB filters for details
            if filters.min_square_footage:
                query = query.gte(
                    "details->>square_footage", filters.min_square_footage
                )

            if filters.max_square_footage:
                query = query.lte(
                    "details->>square_footage", filters.max_square_footage
                )

            if filters.min_year_built:
                query = query.gte("details->>year_built", filters.min_year_built)

            if filters.max_year_built:
                query = query.lte("details->>year_built", filters.max_year_built)

            # Apply amenities filter
            if filters.amenities:
                for amenity in filters.amenities:
                    query = query.contains("amenities", [amenity])

            # Apply group filter
            if filters.group_id:
                group_properties = (
                    self.supabase.table("property_group_members")
                    .select("property_id")
                    .eq("group_id", str(filters.group_id))
                    .execute()
                )

                property_ids = [p["property_id"] for p in group_properties.data]
                if property_ids:
                    query = query.in_("id", property_ids)
                else:
                    return [], 0  # No properties in group

            # Apply pagination
            offset = (page - 1) * per_page
            query = query.range(offset, offset + per_page - 1)

            # Order by updated_at
            query = query.order("updated_at", desc=True)

            # Execute query
            result = query.execute()

            properties = [Property(**p) for p in result.data]
            total = result.count or 0

            return properties, total

        except Exception as e:
            logger.error(f"Error fetching properties: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch properties: {str(e)}",
            )

    async def get_property(self, property_id: UUID, user_id: UUID) -> Property:
        """Get a single property by ID."""
        try:
            result = (
                self.supabase.table("properties")
                .select("*")
                .eq("id", str(property_id))
                .eq("deleted_at", None)
                .execute()
            )

            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Property not found"
                )

            return Property(**result.data[0])

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching property: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch property: {str(e)}",
            )

    async def update_property(
        self, property_id: UUID, data: PropertyUpdate, user_id: UUID
    ) -> Property:
        """Update an existing property."""
        try:
            # Get existing property
            existing = await self.get_property(property_id, user_id)

            # Prepare update data
            update_dict = data.dict(exclude_unset=True, exclude_none=True)

            # Geocode if address changed
            if any(k in update_dict for k in ["address", "city", "state", "zip"]):
                address_parts = [
                    update_dict.get("address", existing.address),
                    update_dict.get("city", existing.city),
                    update_dict.get("state", existing.state),
                    update_dict.get("zip", existing.zip),
                ]
                coords = await self._geocode_address(", ".join(address_parts))
                if coords:
                    update_dict["coordinates"] = (
                        f"POINT({coords.longitude} {coords.latitude})"
                    )

            # Convert complex types
            if "details" in update_dict:
                update_dict["details"] = update_dict["details"].dict(exclude_none=True)
            if "photos" in update_dict:
                update_dict["photos"] = [
                    photo.dict() for photo in update_dict["photos"]
                ]

            # Update property
            result = (
                self.supabase.table("properties")
                .update(update_dict)
                .eq("id", str(property_id))
                .execute()
            )

            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update property",
                )

            # Log audit
            await self._log_audit(
                property_id=property_id,
                action="updated",
                changes=update_dict,
                user_id=user_id,
            )

            return Property(**result.data[0])

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating property: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update property: {str(e)}",
            )

    async def delete_property(
        self, property_id: UUID, user_id: UUID, hard_delete: bool = False
    ) -> bool:
        """Delete a property (soft delete by default)."""
        try:
            if hard_delete:
                # Permanent deletion
                result = (
                    self.supabase.table("properties")
                    .delete()
                    .eq("id", str(property_id))
                    .execute()
                )
            else:
                # Soft delete
                result = (
                    self.supabase.table("properties")
                    .update(
                        {
                            "deleted_at": datetime.now().isoformat(),
                            "status": PropertyStatus.ARCHIVED.value,
                        }
                    )
                    .eq("id", str(property_id))
                    .execute()
                )

            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Property not found"
                )

            # Log audit
            await self._log_audit(
                property_id=property_id,
                action="deleted" if hard_delete else "archived",
                changes={"hard_delete": hard_delete},
                user_id=user_id,
            )

            return True

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting property: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete property: {str(e)}",
            )

    async def bulk_create_properties(
        self, data: PropertyBulkCreate, user_id: UUID
    ) -> Dict[str, Any]:
        """Create multiple properties at once."""
        successful = 0
        failed = 0
        errors = []
        created_ids = []

        for idx, property_data in enumerate(data.properties):
            try:
                property = await self.create_property(property_data, user_id)
                successful += 1
                created_ids.append(property.id)
            except HTTPException as e:
                failed += 1
                if (
                    not data.skip_duplicates
                    or e.status_code != status.HTTP_409_CONFLICT
                ):
                    errors.append(
                        {
                            "index": idx,
                            "address": property_data.address,
                            "error": e.detail,
                        }
                    )
            except Exception as e:
                failed += 1
                errors.append(
                    {"index": idx, "address": property_data.address, "error": str(e)}
                )

        return {
            "successful": successful,
            "failed": failed,
            "errors": errors,
            "created_ids": created_ids,
        }

    # Property Group Methods

    async def create_property_group(
        self, data: PropertyGroupCreate, user_id: UUID
    ) -> PropertyGroup:
        """Create a new property group."""
        try:
            # Check for duplicate name
            existing = (
                self.supabase.table("property_groups")
                .select("id")
                .eq("organization_id", str(data.organization_id))
                .eq("name", data.name)
                .execute()
            )

            if existing.data:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Group with this name already exists",
                )

            # Create group
            group_data = {
                "organization_id": str(data.organization_id),
                "name": data.name,
                "description": data.description,
                "created_by": str(user_id),
            }

            result = self.supabase.table("property_groups").insert(group_data).execute()

            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create property group",
                )

            group = PropertyGroup(**result.data[0])

            # Add initial properties if provided
            if data.property_ids:
                await self.add_properties_to_group(group.id, data.property_ids, user_id)

            return group

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating property group: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create property group: {str(e)}",
            )

    async def add_properties_to_group(
        self, group_id: UUID, property_ids: List[UUID], user_id: UUID
    ) -> int:
        """Add properties to a group."""
        try:
            members = [
                {
                    "group_id": str(group_id),
                    "property_id": str(pid),
                    "added_by": str(user_id),
                }
                for pid in property_ids
            ]

            result = (
                self.supabase.table("property_group_members").upsert(members).execute()
            )

            return len(result.data)

        except Exception as e:
            logger.error(f"Error adding properties to group: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to add properties to group: {str(e)}",
            )

    # Helper Methods

    async def _geocode_address(self, address: str) -> Optional[PropertyCoordinates]:
        """Geocode an address to coordinates."""
        if not self.geocoding_api_key:
            return None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://maps.googleapis.com/maps/api/geocode/json",
                    params={"address": address, "key": self.geocoding_api_key},
                )

                if response.status_code == 200:
                    data = response.json()
                    if data["status"] == "OK" and data["results"]:
                        location = data["results"][0]["geometry"]["location"]
                        return PropertyCoordinates(
                            latitude=location["lat"], longitude=location["lng"]
                        )
        except Exception as e:
            logger.warning(f"Geocoding failed for {address}: {str(e)}")

        return None

    async def _log_audit(
        self, property_id: UUID, action: str, changes: Dict[str, Any], user_id: UUID
    ) -> None:
        """Log property changes to audit table."""
        try:
            self.supabase.table("property_audit_log").insert(
                {
                    "property_id": str(property_id),
                    "action": action,
                    "changes": json.dumps(changes, default=str),
                    "performed_by": str(user_id),
                }
            ).execute()
        except Exception as e:
            logger.warning(f"Failed to log audit: {str(e)}")
